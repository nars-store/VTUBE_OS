# VTUBE Connect Android (Alpha source)

This is the native Android companion source project included with VTUBE OS. It is not a prebuilt APK. Build it using Android Studio with JDK 17, Android SDK 35, and network access for Gradle dependencies.

## Current prototype
- Native Android UI and CameraX front-camera preview.
- Local-network MJPEG endpoint (`/camera.mjpeg?token=...`).
- Microphone PCM endpoint (`/audio.pcm?token=...`) at 16 kHz mono s16le. In Linux use `ffplay -f s16le -ar 16000 -ac 1 http://PHONE_IP:8765/audio.pcm?token=CODE` (shells may require quoting URL).
- Token-gated local status/control endpoint.
- Stop button unbinds camera and stops local server/audio.

## Pair with VTUBE OS
1. Connect phone and Linux laptop to the same trusted Wi-Fi network.
2. Build/install the Android app, open it, grant Camera and Microphone permission, tap Start.
3. Copy the URL shown in the app into VTUBE OS → VTUBE Connect Hub → Open stream. For camera preview use `http://PHONE_IP:8765/camera.mjpeg?token=CODE`.
4. For audio, in a terminal run: `ffplay -f s16le -ar 16000 -ac 1 'http://PHONE_IP:8765/audio.pcm?token=CODE'`. This is a raw PCM test stream; integration into the OS mixer is still required.

## Important limits and safety
- Alpha, unreviewed prototype; do not expose port 8765 to the public internet or use on untrusted Wi-Fi. The code uses a short pairing token and does not yet provide production-grade TLS/encryption, certificate pinning, relay, or robust multi-client handling.
- MJPEG frame conversion is device-dependent and must be tested on real Android phones. Some phone/network configurations may block local traffic.
- Android screen/game capture requires MediaProjection permission flow and is not implemented in this source version. Face tracking, VRM/Live2D, background service, reconnection, and production remote control remain roadmap items.
