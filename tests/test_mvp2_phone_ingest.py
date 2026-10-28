#!/usr/bin/env python3
"""MVP2: receive VTUBE Connect phone streams on the laptop and validate FFmpeg ingest.

This milestone proves the laptop can ingest the phone's camera, screen, or microphone
streams from the same local network using the VTUBE Connect endpoints and optional FFmpeg
pipeline validation.

Examples:
    python3 tools/mvp2_phone_ingest.py --host 192.168.1.42 --token ABC123 --source camera --duration 5
    python3 tools/mvp2_phone_ingest.py --host 192.168.1.42 --token ABC123 --source screen --duration 5
    python3 tools/mvp2_phone_ingest.py --host 192.168.1.42 --token ABC123 --source audio --duration 3
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


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


def ffmpeg_available() -> bool:
    return subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def stream_probe(host: str, token: str, source: str, duration_seconds: int = 5, output_dir: Path | None = None) -> dict:
    """Probe the phone stream with FFmpeg and save a sample if possible."""
    if not ffmpeg_available():
        raise RuntimeError("FFmpeg tidak ditemukan. Instal ffmpeg sebelum menjalankan MVP2.")

    source_map = {"camera": "camera.mjpeg", "screen": "screen.mjpeg", "audio": "audio.pcm"}
    endpoint = source_map[source]
    url = phone_url(host, token, endpoint)

    out_dir = output_dir or Path(tempfile.mkdtemp(prefix="vtube_mvp2_"))
    out_dir.mkdir(parents=True, exist_ok=True)

    if source in {"camera", "screen"}:
        out_file = out_dir / f"{source}_probe.mp4"
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "mjpeg",
            "-i",
            url,
            "-t",
            str(duration_seconds),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out_file),
        ]
    else:
        out_file = out_dir / "audio_probe.wav"
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-i",
            url,
            "-t",
            str(duration_seconds),
            "-c:a",
            "pcm_s16le",
            str(out_file),
        ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg gagal untuk sumber {source}: {result.stderr.strip() or result.stdout.strip()}")

    if not out_file.exists() or out_file.stat().st_size == 0:
        raise RuntimeError(f"Tidak ada sample yang dihasilkan untuk sumber {source}.")

    return {
        "status": "ok",
        "source": source,
        "endpoint": endpoint,
        "url": url,
        "output": str(out_file),
        "size_bytes": out_file.stat().st_size,
        "duration_seconds": duration_seconds,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MVP2 phone-to-laptop ingest validation for VTUBE OS")
    parser.add_argument("--host", required=True, help="Smartphone IPv4 on the same trusted LAN")
    parser.add_argument("--token", required=True, help="6-character VTUBE Connect pairing code")
    parser.add_argument("--source", choices=("camera", "screen", "audio"), default="camera")
    parser.add_argument("--duration", type=int, default=5, help="Probe duration in seconds")
    parser.add_argument("--save-dir", default="./mvp2-output", help="Directory for sample outputs")
    args = parser.parse_args()

    try:
        status = fetch_status(args.host, args.token)
        print(json.dumps({"status": "ok", "payload": status}, indent=2))

        result = stream_probe(args.host, args.token, args.source, args.duration, Path(args.save_dir))
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(f"MVP2 phone ingest failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# End of file
