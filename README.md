# VTUBE OS

VTUBE OS is an experimental VTuber runtime for creator workflows: live face tracking, multi-source compositing, avatar customization, and streaming to OBS / RTMP / YouTube.

This project is structured around a real VTuber pipeline instead of flat SVG placeholders.

## What is supported

- Real VTuber model loading for Live2D and VRM-compatible workflows
- Avatar customization for hair color, eye color, outfit, accent, expression, and pose
- Multi-source composite scene for webcam, phone camera, phone screen, and avatar layer
- Stream target configuration for OBS / RTMP / YouTube
- Original-character workflow with template-based customization

## Folder layout

- `assets/avatars/` — original model and customization assets
- `vtube_avatar_editor.py` — edit the avatar palette and outfit while keeping rigging intact
- `vtube_live2d_renderer.py` — adapter for Live2D Cubism rendering backend
- `vtube_vrm_renderer.py` — adapter for VRM rendering backend
- `vtube_multisource_runtime.py` — compose webcam + phone cam + phone screen + avatar into one scene
- `vtube_stream_output.py` — RTMP / YouTube / OBS streaming helpers

## Original-character policy

Use original, licensed, or properly authorized VTuber model assets. The template editor is intended to create a distinct original character identity while preserving rigging and animation structure.

## Example workflow

1. Put a real Live2D or VRM model in `assets/avatars/`
2. Load the template from `assets/avatars/template_avatar.json`
3. Customize the color palette, outfit, and facial features
4. Build the multi-source live scene
5. Push the final composite to OBS / RTMP / YouTube

## Notes

A real renderer such as Live2D Cubism Web SDK or a VRM-capable Three.js runtime is required for final visual projection. This repository provides the orchestration, customization, and streaming layer; the actual visual engine should be connected to the renderer adapter files above.
