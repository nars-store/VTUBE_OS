# VTUBE OS Alpha Starter

VTUBE OS is an experimental Debian-based VTuber OS environment for anime-style live streaming, avatar creation, and creator workflows. It is designed to be a practical starter platform for local streaming, multi-source capture, and live overlay generation with OBS/RTMP/YouTube support.

This repo has been upgraded with a more polished anime VTuber character system, stronger stream profile presets, and a cleaner setup path for using the project directly from the repository.

## Upgrade highlights

- Improved anime-inspired VTuber character pack with more premium templates and 3D-ready styling metadata.
- Ready-to-use streaming presets for OBS Studio, YouTube Live, Twitch, and custom RTMP targets.
- Live overlay generation with better layout, donation panel, and avatar presentation.
- Realistically styled VTuber characters built from layered vector art, not crude flat SVG placeholders.
- Easy local reproduction from the repo without requiring a separate custom asset pipeline.

## Included features

- VTUBE Control Center with Live Studio, Avatar Studio, Audio Studio, Donation Center, and VTUBE Connect Hub.
- Anime VTuber character templates such as Luna, Nova, Kiro, Aoi, Mika, and Yuzu.
- Live overlay output suitable for OBS capture or direct RTMP broadcast.
- Video sources: VTUBE Connect phone screen or camera, Linux V4L2 webcam/capture device, or X11 desktop capture.
- Audio sources: VTUBE Connect phone microphone, default system mic, or silence.
- Donation goal panel and optional QR code overlay.
- RTMP target profiles for YouTube Live, Twitch, and custom RTMP servers.

## Streaming to OBS / RTMP / YouTube

Use the included stream profiles in `vtube_stream_profiles.py` and the live generator in `vtube_live.py`.

Typical setup:

1. Choose a VTuber preset from `vtube_avatar.py`.
2. Render the live overlay PNG.
3. Select a target profile (OBS / YouTube / Twitch / custom RTMP).
4. Start FFmpeg streaming with the configured video and audio source.
5. Capture the stream inside OBS browser-source or output it directly as RTMP to YouTube.

Examples:

- YouTube: `rtmp://a.rtmp.youtube.com/live2`
- Twitch: `rtmp://live.twitch.tv/app`
- OBS local: `rtmp://127.0.0.1:1935/live`

See `docs/VTUBER_STREAMING_GUIDE.md` for step-by-step setup.

## VTuber 3D-ready design direction

The avatar system now uses a more stylized anime VTuber direction with layered geometry, richer shading, premium color palettes, and metadata that is compatible with future 3D/2.5D rigging workflows. The project is not a full 3D engine by itself, but the starter character pack is designed to feel much closer to mainstream VTuber models than the earlier flat placeholder style.

## Quick start

```bash
python3 -m unittest discover -s tests -v
python3 -c "from vtube_avatar import new_character, render_avatar_svg; print(render_avatar_svg(new_character('Aoi', 'Aoi Live'))[:200])"
```

## Repository structure

- `vtube_avatar.py` — character templates and anime VTuber rendering
- `vtube_live.py` — FFmpeg streaming command builder
- `vtube_stream_profiles.py` — OBS / RTMP / YouTube presets
- `docs/VTUBER_STREAMING_GUIDE.md` — streaming setup guide
- `tests/` — validation tests

## Notes

This repo remains a starter project. It includes a more premium VTuber starter pack and stronger live-streaming profiles, but real-world broadcast quality still depends on your hardware, software, FFmpeg, and network environment.
