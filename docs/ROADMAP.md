# VTUBE OS Roadmap

## Included as prototypes
- Branded Control Center with Live Studio, Avatar Studio, Audio Studio,
  Donation Center and VTUBE Connect Hub.
- Static 2D Luna/Nova/Kiro illustration editor with visual preview, color and
  style customization, local save/load and SVG export.
- Internal FFmpeg RTMP/RTMPS pipeline with one video source, one audio source
  and a transparent avatar/donation overlay.
- Android companion source for camera, consent-based screen sharing and phone
  microphone streams over a trusted local network.
- Debian Live image definition and GitHub Actions workflows for ISO and debug
  APK artifacts.

## Not yet implemented or validated
- Build the OS ISO in GitHub Actions, inspect its artifact and boot it in a VM
  before attempting hardware installation.
- Build the Android debug APK in GitHub Actions, install it and test screen,
  camera and audio capture on the target phone.
- Validate RTMP/RTMPS output with each target platform, along with device
  compatibility, reconnection, CPU usage, network behavior and A/V sync.
- Use the Live Studio canvas as the actual multi-source compositor; currently
  only the selected source and generated avatar/donation overlay are encoded.
- Add rigged/animated avatar support (Live2D/VRM), face/hand tracking,
  expression mapping and lip-sync.
- Add recording, multi-source scene control, per-source audio mixer/effects
  and synchronization.
- Add real donation events only through authorized/official interfaces;
  Saweria goal/link/QR are currently manually displayed, not payment processing.
- Harden Android pairing, encrypted transport, updates, installer/recovery,
  backup, privacy and security before production use.

Use the GitHub Actions workflows for builds rather than building the ISO on a
low-powered local laptop. This repository does not yet contain a tested ISO or
APK.
