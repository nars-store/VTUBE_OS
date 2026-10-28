#!/usr/bin/env python3
"""MVP1: validate VTUBE Connect phone capture endpoints.

This is a lightweight helper for the first milestone: make sure the Android phone is
available on the same local network and can stream camera, screen, or microphone data
into VTUBE OS.

Examples:
    python3 tools/mvp1_phone_capture.py --host 192.168.1.42 --token ABC123 --source camera --save-dir ./mvp1
    python3 tools/mvp1_phone_capture.py --host 192.168.1.42 --token ABC123 --source screen --save-dir ./mvp1
    python3 tools/mvp1_phone_capture.py --host 192.168.1.42 --token ABC123 --source audio --save-dir ./mvp1 --duration 3
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


def phone_url(host: str, token: str, endpoint: str) -> str:
    """Build the VTUBE Connect endpoint URL for a given mobile source."""
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


def extract_jpeg_from_mjpeg(data: bytes) -> bytes | None:
    """Take the first JPEG frame from a raw MJPEG byte stream."""
    if b"\xff\xd8" not in data or b"\xff\xd9" not in data:
        return None

    start = data.index(b"\xff\xd8")
    end = data.index(b"\xff\xd9", start) + 2
    return data[start:end]


def save_first_frame(host: str, token: str, source: str, out_path: Path, timeout: int = 10) -> bool:
    """Capture one JPEG frame from the phone camera or phone screen."""
    endpoint = "camera.mjpeg" if source == "camera" else "screen.mjpeg"
    buffer = bytearray()
    url = phone_url(host, token, endpoint)

    with urllib.request.urlopen(url, timeout=timeout) as response:
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            buffer.extend(chunk)
            frame = extract_jpeg_from_mjpeg(bytes(buffer))
            if frame:
                out_path.write_bytes(frame)
                return True

    return False


def save_audio_sample(host: str, token: str, out_path: Path, duration_seconds: int = 3) -> int:
    """Fetch a short PCM sample from the phone mic."""
    url = phone_url(host, token, "audio.pcm")
    total = 0
    with urllib.request.urlopen(url, timeout=10) as response:
        start = __import__("time").time()
        while True:
            chunk = response.read(4096)
            if not chunk:
                break
            total += len(chunk)
            out_path.write_bytes(chunk) if out_path.exists() is False else None
            if out_path.exists() and out_path.stat().st_size > 0:
                # Keep append mode for streaming capture.
                pass
            if __import__("time").time() - start >= duration_seconds:
                break

    if not out_path.exists():
        out_path.write_bytes(b"")
    return total


def capture_audio(host: str, token: str, out_path: Path, duration_seconds: int = 3) -> int:
    """Capture PCM audio into a file while streaming, with append semantics."""
    url = phone_url(host, token, "audio.pcm")
    total = 0
    start = __import__("time").time()
    with urllib.request.urlopen(url, timeout=10) as response:
        with out_path.open("wb") as handle:
            while True:
                chunk = response.read(4096)
                if not chunk:
                    break
                handle.write(chunk)
                total += len(chunk)
                if __import__("time").time() - start >= duration_seconds:
                    break
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="MVP1 mobile capture validation for VTUBE OS")
    parser.add_argument("--host", required=True, help="Smartphone IPv4 on the same trusted LAN")
    parser.add_argument("--token", required=True, help="6-character VTUBE Connect pairing code")
    parser.add_argument("--source", choices=("camera", "screen", "audio"), default="camera")
    parser.add_argument("--save-dir", default="./mvp1-output", help="Directory for captured samples")
    parser.add_argument("--duration", type=int, default=3, help="Audio capture duration in seconds")
    args = parser.parse_args()

    out_dir = Path(args.save_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        status = fetch_status(args.host, args.token)
        print(json.dumps({"status": "ok", "payload": status}, indent=2))

        if args.source in {"camera", "screen"}:
            frame_file = out_dir / f"{args.source}_frame.jpg"
            ok = save_first_frame(args.host, args.token, args.source, frame_file)
            if ok:
                print(f"Captured {args.source} frame: {frame_file}")
            else:
                raise RuntimeError(f"Tidak berhasil membaca frame dari {args.source}.")
        else:
            audio_file = out_dir / "phone_mic.pcm"
            bytes_written = capture_audio(args.host, args.token, audio_file, duration_seconds=args.duration)
            print(f"Captured PCM audio: {audio_file} ({bytes_written} bytes)")

        return 0
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(f"MVP1 phone capture failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# End of file










































	
	
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		









































































































































































































































































































































































































































































n






































n


nome

















"""







































n
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			"""










































































n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n



















n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n

n
