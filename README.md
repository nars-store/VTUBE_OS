# VTUBE OS Alpha Starter

VTUBE OS is an experimental Debian Live Linux environment for VTuber creation
and streaming. Build artifacts are produced by GitHub Actions; this repository
does not include a prebuilt ISO or Android APK.

## What is included

- VTUBE Control Center with Live Studio, Avatar Studio, Audio Studio, Donation
  Center and VTUBE Connect Hub.
- Original 2D Luna, Nova and Kiro avatar illustrations, a visible editor
  preview, customizable colors/clothing/hair/expressions, local save/load and
  transparent SVG export.
- An in-app live pipeline using FFmpeg internally to compose one video source
  with the selected avatar/donation overlay and send it to an RTMP/RTMPS
  destination. The user controls it from VTUBE Live Studio; no separate
  broadcasting application is part of the workflow.
- Video sources: VTUBE Connect phone screen or camera, Linux V4L2 webcam/capture
  device, or X11 desktop capture. Audio sources: VTUBE Connect phone microphone,
  the system's default microphone, or silence.
- Donation goal, Saweria link and optional PNG/JPEG QR image in the live
  overlay. These are display elements only; payment events and automatic goal
  updates are not integrated.
- VTUBE Connect Android source project with CameraX, consent-based
  MediaProjection screen sharing, and local token-gated video/audio endpoints.

The engine, Android transport and overlay are prototypes. The avatar is a
static 2D illustration: facial tracking, lip-sync, Live2D/VRM animation and
hand tracking are not implemented. The Live Studio canvas is a layout mockup;
its draggable placeholder elements are not yet sent to the live output.
Streaming performance, audio synchronization and device compatibility have
not yet been verified on physical hardware.

## Build VTUBE OS on GitHub Actions

Push this repository to GitHub and run **Build VTUBE OS ISO** from the Actions
tab (or push to `main`). Download the ISO and checksum from the completed
workflow artifact. Test the ISO in a virtual machine before installing or
using it on hardware. No local ISO build is required.

The workflow performs source syntax checks and unit tests before building.
The image includes FFmpeg and CairoSVG as internal media/rendering components;
it does not install OBS Studio.

## Build VTUBE Connect APK on GitHub Actions

The **Build VTUBE Connect Android APK** workflow runs when Android source files
change on `main`, or can be started manually from the Actions tab. Download
`VTUBE-Connect-debug-APK` from the completed run and install it on the phone.

Connect the phone and VTUBE OS laptop to the same trusted local network. Start
VTUBE Connect, grant the requested camera/microphone permissions, and use
**Share phone screen** with Android's system consent prompt when sending phone
gameplay. Enter the phone IP and pair code in **VTUBE Connect Hub**, then select
the phone screen/camera and microphone in **VTUBE Live Studio**. Never expose
the Android endpoint port to the public internet.

## Live streaming setup

In VTUBE Live Studio, choose a video/audio source, resolution, frame rate and
bitrate; enter the streaming platform's RTMP/RTMPS server and stream key; then
select **Start VTUBE live**. The media engine and video composition run inside
VTUBE OS. The platform supplies the ingest URL and key. Stream settings,
including the key, are kept in the user's local configuration with
owner-only file permissions; they are not encrypted.

Donation Center can display a manually configured goal, Saweria link and
optional PNG/JPEG QR code. It does not process donations, verify payments,
receive Saweria events or update totals automatically. Only the currently
selected source plus the static avatar/donation overlay is encoded; the
placeholder scene canvas is not yet a live compositor.

## Development and validation status

Run the lightweight test suite with `python3 -m unittest discover -s tests -v`.
The ISO build, Android build, live RTMP transmission and physical Android
capture have not been run/verified in this environment. Check the GitHub
Actions results and test on a VM and real devices before relying on them.
