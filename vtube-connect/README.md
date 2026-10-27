# VTUBE Connect — Android companion

Native Kotlin Android source is under `android/`; the project does not include a prebuilt APK.

Current prototype: CameraX webcam feed, raw PCM microphone endpoint, token-gated local MJPEG/control endpoints, and Android MediaProjection screen sharing after explicit user consent.

Build/install the APK with Android Studio, JDK 17 and Android SDK 35. Camera, screen, and audio streams currently require the phone and VTUBE OS to share a trusted local network. See `android/README.md` for the setup steps.

Transport roadmap:
- USB/local transport where supported
- LAN discovery and pairing using a one-time code
- Encrypted control and media sessions
- Internet Anywhere mode using encrypted direct connectivity or a relay
- Explicit camera/microphone/screen-capture permissions, revocable pairing, no hidden capture

Protected screen content may not be capturable. Phone audio capture varies by device and Android version. USB and internet Anywhere modes remain future work.
