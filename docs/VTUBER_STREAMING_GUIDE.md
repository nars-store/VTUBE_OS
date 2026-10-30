# VTUBER Streaming Guide

This guide explains how to use the upgraded VTUBE OS starter with anime VTuber templates, OBS integration, RTMP output, and YouTube streaming.

## 1. Choose a character template

Open `vtube_avatar.py` and select one of these templates:

- Luna
- Nova
- Kiro
- Aoi
- Mika
- Yuzu

Example:

```python
from vtube_avatar import new_character, render_avatar_svg

character = new_character("Aoi", "Aoi Live")
svg = render_avatar_svg(character)
print(svg[:200])
```

## 2. Render the live overlay

The stream overlay is generated with `render_stream_overlay_svg()`. This outputs a transparent/clean overlay layout designed for OBS or direct capture.

## 3. Select a streaming profile

Use `vtube_stream_profiles.py` to pick a target:

```python
from vtube_stream_profiles import get_stream_profile

profile = get_stream_profile("YOUTUBE")
print(profile.endpoint)
print(profile.stream_key)
```

Available profiles:

- OBS
- YOUTUBE
- TWITCH
- CUSTOM

## 4. Streaming into OBS

1. Open OBS Studio.
2. Add a source for your webcam or capture card.
3. Add your VTUBE overlay as a browser source or image source.
4. Set the video source and audio source from VTUBE OS or your capture setup.
5. Configure final output stream to `rtmp://...` if required.

## 5. RTMP / YouTube

Use the generated FFmpeg command from `vtube_live.py` or run your stream via OBS to YouTube with the provided target values.

Recommended stream values:

- Resolution: 1920x1080
- FPS: 30
- Bitrate: 4500 kbps
- Encoder: H.264

## 6. Notes

- YouTube requires a valid stream key from the YouTube Live dashboard.
- OBS is the easiest local setup for preview and broadcast control.
- Real stream quality depends on your internet connection, GPU, and capture device.

## 7. Character style direction

The upgraded VTuber templates aim for a more polished anime-inspired look and a cleaner 3D-ready presentation, closer to modern streamer avatar packs than the older flat placeholder design.
