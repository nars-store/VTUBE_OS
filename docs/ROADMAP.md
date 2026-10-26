# VTUBE OS Roadmap (Alpha 0.2)

## Included now
- Python/Tkinter branded control center, scene placeholder canvas, local profiles, avatar color/preset UI, donation goal + simulated alert.
- Linux camera discovery (`/dev/video*`) and ffplay preview, audio source/sink enumeration and default-device selection via PipeWire/PulseAudio tools.
- Input-mode selector for webcam, capture card, phone/IP camera, external mic and mobile-gaming workflows.
- Native Android companion source project in `vtube-connect/android`, including CameraX preview and token-gated local MJPEG/raw-PCM endpoints.
- Debian Live ISO build script, package list, desktop autostart. ISO must be built on a Debian/Ubuntu host and tested; no ISO binary is prebuilt in this archive.

## Not yet production-ready
- The live canvas is not a real-time video compositor; no integrated encoder/record/stream pipeline yet.
- VRM/Live2D rendering, face/hand tracking, actual avatar assets and expression mapping.
- Android screen/game capture (MediaProjection), reliable USB transport, encrypted internet relay, automatic reconnect, full remote control and hardened pairing.
- Per-source audio mixer/effects/sync and seamless phone mic injection into the OS mixer.
- Real Saweria payment/webhook integration and supported chat integrations for YouTube/Twitch/TikTok. Platform APIs, authentication, permissions and current policies must be verified before implementation. Donation alert is simulation only.
- Installer validation, secure updates, backup/restore, diagnostics, plugin sandbox and privacy review.

## Next milestone order
1. Test and harden Android local camera/audio streams on physical devices; integrate into GStreamer/FFmpeg and source selection.
2. Replace canvas mockup with a GStreamer compositor and FFmpeg recording/streaming backend.
3. Add supported avatar renderer and tracking backend.
4. Implement platform integrations through official/authorized APIs and donation provider's supported webhook/API.
5. Harden pairing, privacy indicators, firewall defaults, updates, installer and recovery.
