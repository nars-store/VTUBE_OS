# VTUBE OS Feature Matrix

“Implemented” describes a prototype in this source tree; it does not imply
validation on a completed ISO, phone or live streaming platform.

| Area | Included in the prototype | Status / limitation |
|---|---|---|
| VTUBE OS Control Center | Dashboard, navigation, profiles and settings | Debian Live image has not yet been built/tested |
| VTUBE desktop applications | App-menu entries for Live Studio, Avatar Studio, Audio Studio, Donation Center and Connect Hub | Launch the shared Control Center at the selected page |
| Live Studio | Internal FFmpeg pipeline, RTMP/RTMPS destination, source selectors, resolution/FPS/bitrate, start/stop and engine log | Not yet tested against a live platform; stream key is locally stored but not encrypted |
| Live video sources | Phone screen/camera MJPEG, Linux V4L2 devices, or X11 desktop capture | One selected source at a time; the scene canvas placeholders do not feed the stream |
| Live audio sources | Phone microphone PCM, default system microphone, or silence | No per-source mixer/effects or verified A/V synchronization |
| 2D Avatar Studio | Original Luna/Nova/Kiro illustrations; visual preview; hair, eye, skin and clothing colors; outfits, hair styles and expressions; save/load JSON; SVG export | Static illustration; no rigging, face tracking, lip-sync or animation |
| 3D Avatar Studio | VRM/Live2D compatibility target | No 3D renderer, rigging or tracking |
| Phone connection | Android companion source; LAN pairing, token-protected endpoints, CameraX camera, MediaProjection screen and microphone PCM | Experimental; physical device and network testing required; no public relay/TLS |
| Donation Center | Manual goal, Saweria URL, PNG/JPEG QR image and test alert; values appear in overlay | No payment processing, webhook, verified alert or automatic goal progress |
| Privacy/security | Android permissions and stop control; stream settings owner-only | Prototype security only; local network only, stream key not encrypted, needs hardening |
| Chat/platform integrations | Planned | No YouTube/Twitch/TikTok chat or platform API integration |
| Bootable OS | Debian Live build script and GitHub Actions ISO workflow | ISO is not prebuilt or validated |
| Android app | Android Studio source and GitHub Actions debug APK workflow | APK build and real-phone use require verification from Actions/device testing |
