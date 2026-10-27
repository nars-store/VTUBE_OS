# VTUBE OS architecture

- **VTUBE desktop app (`app.py`)**: Control Center with Live Studio, Avatar
  Studio, Audio Studio, Donation Center and Connect Hub pages. Debian Live
  installs desktop launchers that open the shared app at a selected page.
- **Live Studio**: Starts and stops an internal FFmpeg process. It accepts a
  single video input (phone MJPEG, V4L2 or X11), one audio input (phone PCM,
  PulseAudio default source or silence), a generated transparent PNG overlay,
  and RTMP/RTMPS output. The live scene canvas remains a UI mockup and does not
  control the encoded composition.
- **Avatar Studio**: Original static 2D SVG templates, editor preview and
  local character JSON under `~/.config/vtube-os/characters/`. A generated
  SVG combines the selected avatar with the manually configured donation goal,
  URL and optional QR image; CairoSVG renders it for FFmpeg.
- **Settings and credentials**: Stream settings live in
  `~/.config/vtube-os/stream-settings.json` with owner-only permissions.
  Stream keys are not encrypted. Logs are written to the same user's
  configuration directory.
- **VTUBE Connect Android**: Android companion in `vtube-connect/android`.
  CameraX, user-approved MediaProjection and AudioRecord serve local
  token-gated MJPEG/PCM endpoints. VTUBE Live Studio consumes those endpoints
  directly; no separate broadcasting client is needed.
- **OS image**: Debian Live + XFCE, PipeWire, FFmpeg, CairoSVG, V4L2 tools and
  NetworkManager. ISO build and runtime have not yet been verified.
- **Not implemented**: face/hand tracking, avatar animation/lip-sync,
  multi-source scene composition, recording, automatic donation events,
  platform chat, secure remote relay and production installer/update system.

Security boundary: Android streaming is a local-network prototype. Do not
forward port 8765 or use it on an untrusted network. Production use requires
stronger authentication, encrypted transport, firewall policy and review.
