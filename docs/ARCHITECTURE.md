# VTUBE OS architecture

- **Control Center (`app.py`)**: navigation, scene layout mockup, profile state, device discovery and launch actions.
- **Device abstraction (current)**: Linux V4L2 `/dev/video*`; PipeWire/PulseAudio via `pactl`; camera preview via FFmpeg/ffplay.
- **VTUBE Connect Android**: Android Studio project in `vtube-connect/android`. CameraX preview feeds a local token-gated MJPEG endpoint; AudioRecord exposes raw PCM. Local LAN only for this alpha.
- **Media backend (planned)**: GStreamer compositor for camera/game/avatar/overlay, FFmpeg encode/mux, virtual camera/audio routing where supported.
- **Avatar backend (planned)**: VRM/Live2D compatibility layer, face/hand tracking and expression mapper.
- **Platform adapters (planned)**: provider-specific official APIs, OAuth/token storage and webhooks. No credentials stored in source code.
- **System layer**: Debian Live + XFCE, PipeWire, udev/V4L2 and NetworkManager.

Security boundary: current Android transport is prototype-only. Do not forward its port to the public internet. Production release needs TLS/authentication hardening, rate limiting, explicit consent, secure token storage and threat review.
