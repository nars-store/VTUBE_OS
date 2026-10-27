"""Internal FFmpeg live-stream command construction for VTUBE OS."""
import ipaddress
import base64
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.parse import urlsplit

from vtube_avatar import render_stream_overlay_svg


RESOLUTIONS = {
    "1280x720": (1280, 720),
    "1920x1080": (1920, 1080),
}
FRAME_RATES = (24, 30, 60)
VIDEO_BITRATES = {
    "2500 kbps": "2500k",
    "4500 kbps": "4500k",
    "6000 kbps": "6000k",
}
QR_MIME_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def write_stream_overlay(path, character, goal, donation_link="", qr_path=""):
    """Render the transparent VTUBE overlay to PNG for the live media pipeline."""
    qr_data_uri = ""
    if qr_path:
        image_path = Path(qr_path)
        mime_type = QR_MIME_TYPES.get(image_path.suffix.lower())
        if not mime_type:
            raise ValueError("QR overlay hanya mendukung file PNG atau JPEG.")
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        qr_data_uri = f"data:{mime_type};base64,{encoded}"
    svg = render_stream_overlay_svg(character, goal, donation_link, qr_data_uri)
    try:
        import cairosvg
    except ImportError as error:
        raise RuntimeError("Renderer SVG belum tersedia. Pastikan paket VTUBE python3-cairosvg terpasang.") from error
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(path), output_width=1920, output_height=1080)


def phone_stream_url(host, token, endpoint):
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
    if endpoint not in ("screen.mjpeg", "camera.mjpeg", "audio.pcm", "status"):
        raise ValueError("Endpoint VTUBE Connect tidak dikenal.")
    return f"http://{address}:8765/{endpoint}?{urlencode({'token': code})}"


def rtmp_target(server, stream_key):
    server = server.strip().rstrip("/")
    key = stream_key.strip().strip("/")
    parsed = urlsplit(server)
    if (
        parsed.scheme not in ("rtmp", "rtmps")
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not re.fullmatch(r"[A-Za-z0-9._~/-]+", key)
    ):
        raise ValueError("Masukkan alamat RTMP/RTMPS dan stream key yang valid.")
    try:
        parsed.port
    except ValueError as error:
        raise ValueError("Port pada alamat RTMP/RTMPS tidak valid.") from error
    return f"{server}/{key}"


def build_stream_command(
    ffmpeg,
    video_source,
    audio_source,
    target,
    width,
    height,
    fps,
    bitrate,
    overlay_png,
    phone_host="",
    pair_code="",
    camera_device="",
    display="",
    audio_device="default",
):
    if width <= 0 or height <= 0 or fps not in FRAME_RATES:
        raise ValueError("Resolusi atau FPS tidak didukung.")
    if bitrate not in VIDEO_BITRATES.values():
        raise ValueError("Bitrate tidak didukung.")

    command = [ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "warning", "-y"]
    if video_source in ("phone-screen", "phone-camera"):
        endpoint = "screen.mjpeg" if video_source == "phone-screen" else "camera.mjpeg"
        command.extend(["-f", "mpjpeg", "-i", phone_stream_url(phone_host, pair_code, endpoint)])
    elif video_source == "webcam":
        if not camera_device.startswith("/dev/video"):
            raise ValueError("Pilih perangkat kamera Linux /dev/video*.")
        command.extend(["-f", "v4l2", "-framerate", str(fps), "-video_size", f"{width}x{height}", "-i", camera_device])
    elif video_source == "desktop":
        if not display:
            raise ValueError("Desktop capture memerlukan sesi grafis X11 yang aktif.")
        command.extend(["-f", "x11grab", "-framerate", str(fps), "-video_size", f"{width}x{height}", "-i", display])
    else:
        raise ValueError("Sumber video VTUBE tidak dikenal.")

    if audio_source == "phone-mic":
        command.extend(["-f", "s16le", "-ar", "16000", "-ac", "1", "-i",
                        phone_stream_url(phone_host, pair_code, "audio.pcm")])
    elif audio_source == "system-mic":
        command.extend(["-f", "pulse", "-i", audio_device])
    elif audio_source == "none":
        command.extend(["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"])
    else:
        raise ValueError("Sumber audio VTUBE tidak dikenal.")

    audio_index = 1
    command.extend(["-loop", "1", "-framerate", str(fps), "-i", overlay_png])
    graph = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[base];"
        f"[2:v]scale={width}:{height}[overlay];"
        "[base][overlay]overlay=0:0:shortest=1[outv]"
    )
    command.extend([
        "-filter_complex", graph,
        "-map", "[outv]", "-map", f"{audio_index}:a:0",
        "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast",
        "-b:v", bitrate, "-maxrate", bitrate, "-bufsize", str(int(bitrate[:-1]) * 2) + "k",
        "-pix_fmt", "yuv420p", "-g", str(fps * 2),
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
        "-f", "flv", target,
    ])
    return command
