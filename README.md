# VTUBE OS Alpha Starter

VTUBE OS is an experimental VTuber runtime for face-driven live streaming, avatar control, and creator workflows. This version removes the old static SVG avatar prototype and upgrades the project into a real face-tracking-oriented VTuber foundation for Live2D/VRM-style motion control.

## What is new

- Real VTuber rig architecture driven by webcam or phone camera input
- Face tracking pipeline with head pose, blink, eye openness, smile, and mouth motion
- Live2D/VRM-ready avatar model registry and runtime state management
- No more static SVG-only avatar placeholder logic
- Compatible with OBS / RTMP / YouTube streaming workflows

## VTuber runtime model

The project is now built around a face-driven avatar rig:

- Head yaw / pitch / roll is mapped from the face tracker
- Eye openness and blink are mapped to the rig state
- Smile and mouth motion drive expression states
- The rig state can be plugged into a Live2D/VRM implementation or any real avatar engine

This is a real VTuber runtime foundation, but it still requires an actual Live2D or VRM avatar asset file for final visual rendering.

## Streaming support

VTUBE OS still supports the streaming stack for OBS, RTMP, and YouTube outputs using the existing live pipeline and stream profiles.

## Quick start

```bash
python3 -m unittest discover -s tests -v
python3 -c "from vtube_avatar import FaceDrivenAvatarRig; from vtube_expression_mapper import FaceMetrics; rig = FaceDrivenAvatarRig('Aoi'); print(rig.update(FaceMetrics(confidence=0.9, head_yaw=0.2, head_pitch=-0.1, left_eye_open=0.8, right_eye_open=0.8, mouth_open=0.5, smile=0.7, blink=0.05, eyebrow_raise=0.15, source='webcam')).as_dict())"
```

## Notes

- The project is no longer built around static SVG avatar rendering.
- Real visual VTuber fidelity depends on importing a proper Live2D or VRM model asset into the runtime.
- The face-tracking foundation is ready for a real-time avatar engine, webcam, or phone camera workflow.

