# VTUBE OS Alpha Starter 0.2

VTUBE OS is a VTuber-first Linux live environment prototype. The archive contains the OS control-center source, Debian Live ISO build scripts, device/audio tooling, overlays, documentation, and a native Android **VTUBE Connect source project**.

## What's included
- Control Center with Dashboard, Live Studio scene-layout prototype, Avatar Studio preset/customization UI, Audio Studio, Donation Center (simulation), VTUBE Connect Hub, Feature Center, profiles and settings.
- Linux camera discovery and external webcam/capture-card preview via ffplay.
- Microphone/output device enumeration and default selection using PipeWire/PulseAudio.
- Android app source project for CameraX phone camera, local MJPEG stream, raw PCM microphone endpoint and a token-gated local control/status endpoint.
- Debian Live build script and boot-time app setup.

## Run the desktop prototype
```bash
sudo apt update
sudo apt install -y python3 python3-tk ffmpeg pavucontrol
chmod +x run.sh
./run.sh
```

## Build Android app
Open `vtube-connect/android` in Android Studio (JDK 17 and Android SDK 35). Sync Gradle and build APK. This archive contains source code, **not a prebuilt APK**.

On phone: install app, grant Camera/Microphone permissions, tap Start. Put laptop and phone on the same trusted Wi-Fi. Copy the camera URL displayed by the app into VTUBE OS → VTUBE Connect Hub → Open stream. The audio endpoint can be tested with `ffplay -f s16le -ar 16000 -ac 1 'http://PHONE_IP:8765/audio.pcm?token=CODE'`.

## Build bootable ISO (Linux host)
```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso
sudo ./tools/build-iso.sh
```
The script writes the ISO under `build-output/` if the host, mirrors, architecture and package set build successfully. The ISO has **not been built or tested in this environment**; test in QEMU before installing to hardware.

## Important honesty / limitations
This is an alpha development package, not a finished production OS. Live Studio still uses a layout mockup, not a true compositor/streaming engine. Avatar models are presets/placeholders, not a VRM/Live2D renderer. Donation alerts are simulated, not real Saweria payments. Platform chat/live APIs are not connected. Android screen capture, face tracking, USB tether transport, internet relay, production-grade encryption and auto-reconnect are not yet implemented. Android local camera/audio endpoints are experimental; use only on a trusted LAN and do not expose port 8765 to the internet.

See `docs/ROADMAP.md` for the full implementation plan.
