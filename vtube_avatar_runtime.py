# VTUBE OS Alpha Starter

VTUBE OS is an experimental VTuber runtime for face-driven live streaming, avatar control, and creator workflows. This revision consolidates the source around a real VTuber pipeline architecture:

- Live2D and VRM-ready avatar model loading
- multi-source scene layout for webcam, phone camera, phone screen, and mic
- real-time face tracking mapped to motion and expression states
- OBS / RTMP / YouTube streaming readiness

## Avatar model support

The project now expects to load real VTuber assets from `assets/avatars/`.

Accepted model types:
- Live2D Cubism (`.model3.json`)
- VRM (`.vrm`)

The runtime reads `assets/avatars/manifest.json` to discover which characters are available.

## Live scene architecture

The runtime supports multiple input sources simultaneously:
- webcam / laptop camera
- phone camera stream
- phone screen share
- phone microphone input
- avatar character layer
- stream output layer

This is built as a multi-source live scene, not a single-cam pipeline.

## Runtime usage

```bash
python3 -m unittest discover -s tests -v
python3 -c "from vtube_avatar_loader import AvatarAssetLoader; print(AvatarAssetLoader().snapshot())"
```

## Important note

A real VTuber model is still required for final visual fidelity. The project provides the runtime, loader, and scene orchestration for real Live2D/VRM assets; the actual `.vrm` or `.model3.json` character files must be placed in `assets/avatars/`.

