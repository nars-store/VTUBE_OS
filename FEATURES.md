# VTUBE OS Feature Matrix

This file tracks the feature set requested for VTUBE OS. “Included” means a usable prototype control or tool exists; it does not imply a finished broadcast pipeline.

| Area | In this archive | Status / limitation |
|---|---|---|
| VTUBE OS Control Center | Branded dashboard, navigation, profiles, settings | Prototype |
| Live Studio | Scene canvas, movable placeholder elements, scene selection, donation alert test | Layout mockup; compositor/encoder not yet integrated |
| 2D/3D Avatar Studio | Starter presets and color customization | No VRM/Live2D renderer or real model rig yet |
| Face/motion tracking | Architecture and planned integration | Not implemented |
| Webcam/laptop camera | Detect `/dev/video*`; preview through ffplay | Linux-supported devices only |
| External webcam/capture card | Same V4L2 device path | Driver/device compatibility varies |
| External microphone/headset | Detect PipeWire/PulseAudio inputs; set default source | Basic device routing; no per-source effects mixer |
| Phone camera | Android source project provides local MJPEG stream | Experimental, same trusted LAN required |
| Phone microphone | Android source project provides raw PCM endpoint | Testable with ffplay; not yet mixed into built-in Live Studio |
| Phone pairing | Short token for local endpoints | Not production security; no internet relay or TLS yet |
| Mobile gaming/screen capture | Mode choice and roadmap | Android MediaProjection not implemented |
| Scene/overlay studio | Starter HTML alert overlay and scene placeholders | Needs integrated compositor and asset manager |
| Donation center | Goal, simulated donation total and test alert | No real Saweria transactions/webhook |
| YouTube/Twitch/TikTok chat/live | Planned adapter points | Requires supported official APIs, authorization and policy review |
| Profiles/automation | Local profiles and scene selection | Advanced automation/scene triggers pending |
| Privacy/security | Explicit Android permissions and Stop button; local token | Needs security review, hardened auth, TLS and firewall policy |
| Backup/sync/plugins/diagnostics | Roadmap/docs | Not fully implemented |
| Bootable ISO | Debian Live build script | Must be built on Linux; ISO is not prebuilt or validated in this ZIP |
| Android app | Android Studio project source | APK must be built locally; no prebuilt APK in this ZIP |
