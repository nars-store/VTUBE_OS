#!/usr/bin/env python3
"""MVP3: compose a live VTUBE output using a phone source plus overlay.

This milestone closes the loop between the phone capture endpoints and an actual live
stream pipeline. The laptop receives a phone camera or screen stream, optionally mixes
in the phone mic, renders a VTUBE overlay, and sends the final result to either a local
MP4 file or an RTMP/RTMPS destination.

Examples:
    python3 tools/mvp3_phone_live.py \
        --host 192.168.1.42 --token ABC123 --source phone-screen --audio-source phone-mic \
        --output ./mvp3-output/live.mp4 --resolution 1280x720 --fps 30

    python3 tools/mvp3_phone_live.py \
        --host 192.168.1.42 --token ABC123 --source phone-camera --audio-source phone-mic \
        --output rtmp://a.rtmp.youtube.com/live2/KEY --resolution 1280x720 --fps 30
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import cairosvg
except Exception:  # pragma: no cover - optional dependency for rendering overlay PNG
    cairosvg = None

from vtube_avatar import new_character, render_stream_overlay_svg


def phone_url(host: str, token: str, endpoint: str) -> str:
    """Build the VTUBE Connect endpoint URL."""
    address = ipaddress.ip_address(host.strip())
    if (
        address.version != 4
        or not address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
    ):
        raise ValueError("Masukkan IPv4 privat dari jaringan lokal HP dan laptop.")

    code = token.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{6}", code):
        raise ValueError("Pair code harus berisi 6 karakter.")

    allowed = ("screen.mjpeg", "camera.mjpeg", "audio.pcm", "status")
    if endpoint not in allowed:
        raise ValueError("Endpoint VTUBE Connect tidak dikenal.")

    return f"http://{address}:8765/{endpoint}?{urllib.parse.urlencode({'token': code})}"


def fetch_status(host: str, token: str) -> dict:
    with urllib.request.urlopen(phone_url(host, token, "status"), timeout=5) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if data.get("status") != "ok":
        raise RuntimeError(f"Status endpoint tidak valid: {data!r}")
    return data


def render_overlay_png(
    output_path: str | Path,
    character=None,
    goal: int = 100000,
    donation_link: str = "",
    qr_path: str | None = None,
) -> Path:
    """Render a PNG overlay that will be composited into the live stream."""
    if cairosvg is None:
        raise RuntimeError("cairosvg belum terpasang; install python3-cairosvg untuk render overlay.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    avatar = character or new_character("Luna")
    qr_data_uri = ""
    if qr_path and Path(qr_path).is_file():
        suffix = Path(qr_path).suffix.lower()
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(suffix)
        if not mime:
            raise ValueError("QR overlay hanya mendukung file PNG atau JPEG.")
        import base64

        encoded = base64.b64encode(Path(qr_path).read_bytes()).decode("ascii")
        qr_data_uri = f"data:{mime};base64,{encoded}"

    svg = render_stream_overlay_svg(avatar, goal, donation_link, qr_data_uri)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(output), output_width=1920, output_height=1080)
    return output


def build_live_command(
    video_source: str,
    audio_source: str,
    target: str,
    width: int,
    height: int,
    fps: int,
    bitrate: str,
    overlay_png: str,
    phone_host: str = "",
    pair_code: str = "",
    audio_device: str = "default",
    display: str = "",
) -> list[str]:
    """Construct an FFmpeg command for a live VTUBE stream."""
    if width <= 0 or height <= 0:
        raise ValueError("Resolusi harus valid.")
    if fps <= 0:
        raise ValueError("FPS harus lebih besar dari 0.")

    if video_source in {"phone-screen", "phone-camera"}:
        endpoint = "screen.mjpeg" if video_source == "phone-screen" else "camera.mjpeg"
        video_input = phone_url(phone_host, pair_code, endpoint)
        video_fmt = "mjpeg"
        video_args = ["-f", video_fmt, "-i", video_input]
    elif video_source == "desktop":
        if not display:
            raise ValueError("Display X11 harus diisi untuk desktop capture.")
        video_args = [
            "-f",
            "x11grab",
            "-framerate",
            str(fps),
            "-video_size",
            f"{width}x{height}",
            "-i",
            display,
        ]
    elif video_source == "webcam":
        video_args = [
            "-f",
            "v4l2",
            "-framerate",
            str(fps),
            "-video_size",
            f"{width}x{height}",
            "-i",
            "/dev/video0",
        ]
    else:
        raise ValueError(f"Sumber video tidak dikenal: {video_source}")

    if audio_source == "phone-mic":
        audio_input = phone_url(phone_host, pair_code, "audio.pcm")
        audio_args = [
            "-f",
            "s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-i",
            audio_input,
        ]
    elif audio_source == "system-mic":
        audio_args = ["-f", "pulse", "-i", audio_device]
    elif audio_source == "none":
        audio_args = ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    else:
        raise ValueError(f"Sumber audio tidak dikenal: {audio_source}")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-loglevel",
        "warning",
        "-y",
    ]
    command += video_args
    command += audio_args
    command += [
        "-loop",
        "1",
        "-framerate",
        str(fps),
        "-i",
        overlay_png,
    ]

    graph = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[base];"
        f"[2:v]scale={width}:{height}[overlay];"
        "[base][overlay]overlay=0:0:shortest=1[outv]"
    )

    output_format = "flv" if target.startswith(("rtmp://", "rtmps://", "rtsp://")) else "mp4"
    command += [
        "-filter_complex",
        graph,
        "-map",
        "[outv]",
        "-map",
        "1:a:0",
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-b:v",
        bitrate,
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "44100",
        "-f",
        output_format,
        target,
    ]
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="MVP3 live pipeline for VTUBE OS phone-input validation")
    parser.add_argument("--host", required=True, help="IP HP di jaringan lokal yang sama")
    parser.add_argument("--token", required=True, help="Kode pairing 6 karakter VTUBE Connect")
    parser.add_argument("--source", choices=("phone-screen", "phone-camera", "webcam", "desktop"), default="phone-screen")
    parser.add_argument("--audio-source", choices=("phone-mic", "system-mic", "none"), default="phone-mic")
    parser.add_argument("--output", required=True, help="Target output: file .mp4 or RTMP URL")
    parser.add_argument("--resolution", default="1280x720", help="Resolusi input/output, contoh 1280x720")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--bitrate", default="2500k", help="Bitrate FFmpeg, contoh 2500k")
    parser.add_argument("--goal", type=int, default=100000, help="Goal donasi yang ditampilkan di overlay")
    parser.add_argument("--donation-link", default="https://example.com/donate")
    parser.add_argument("--overlay-output", default="./mvp3-output/vtube-overlay.png")
    parser.add_argument("--qr-path", default="")
    parser.add_argument("--display", default="")
    parser.add_argument("--audio-device", default="default")
    args = parser.parse_args()

    try:
        status = fetch_status(args.host, args.token)
        print(json.dumps({"status": "ok", "payload": status}, indent=2))

        width, height = [int(part) for part in args.resolution.lower().split("x", 1)]
        overlay_path = render_overlay_png(
            args.overlay_output,
            goal=args.goal,
            donation_link=args.donation_link,
            qr_path=args.qr_path or None,
        )

        command = build_live_command(
            video_source=args.source,
            audio_source=args.audio_source,
            target=args.output,
            width=width,
            height=height,
            fps=args.fps,
            bitrate=args.bitrate,
            overlay_png=str(overlay_path),
            phone_host=args.host,
            pair_code=args.token,
            audio_device=args.audio_device,
            display=args.display,
        )

        print("FFmpeg command:")
        print(subprocess.list2cmdline(command) if sys.platform.startswith("win") else " ".join(command))
        return 0
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(f"MVP3 live pipeline failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# End of file
