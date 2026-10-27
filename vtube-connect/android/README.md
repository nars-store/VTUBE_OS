# VTUBE Connect Android (Alpha source)

VTUBE Connect is the Android companion source project included with VTUBE OS.
GitHub Actions can build a debug APK; Android Studio with JDK 17 and Android
SDK 35 is an optional local development route.

## Prototype capabilities
- Native Android UI and CameraX camera capture.
- Local-network MJPEG camera endpoint (`/camera.mjpeg?token=...`).
- Explicit Android MediaProjection consent and foreground service for the
  phone screen endpoint (`/screen.mjpeg?token=...`).
- Microphone PCM endpoint (`/audio.pcm?token=...`) at 16 kHz mono s16le.
- Token-gated local status/control endpoint. Stop ends the camera, screen
  sharing, server and microphone stream.

## Use with VTUBE OS
1. Connect the phone and laptop to the same trusted local network.
2. Build/install the debug APK from GitHub Actions, open VTUBE Connect, grant
   the requested permissions and tap **Start**.
3. For phone gameplay, tap **Share phone screen** and approve Android's
   MediaProjection system prompt.
4. Enter the phone IP and pair code in VTUBE OS → **VTUBE Connect Hub**. Check
   the connection or use **Pakai sumber HP di Live Studio**.
5. In **VTUBE Live Studio**, select the phone screen or camera and phone mic,
   configure the platform's RTMP/RTMPS destination, and start the built-in
   VTUBE live engine.

## Limits and safety
- This is an experimental prototype; do not expose port 8765 to the public
  internet or use it on untrusted Wi-Fi. Transport is not production-grade
  encrypted/authenticated.
- MJPEG conversion, Android background behavior, local network access and
  performance vary by device and must be tested on a real phone.
- Screen sharing requires explicit system consent and may show protected
  content as blank.
- Face tracking, avatar motion, USB transport, secure internet relay,
  reconnection and production remote control are not implemented.
