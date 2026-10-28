from __future__ import annotations

from typing import List, Optional


class MediaPipelineBuilder:
    """Build FFmpeg command lines for VTUBE OS input sources."""

    def __init__(self, video_source: str, audio_source: Optional[str] = None, output_target: str = "output.mp4"):
        self.video_source = video_source
        self.audio_source = audio_source
        self.output_target = output_target

    def build(self, width: int = 1280, height: int = 720, fps: int = 30, bitrate: str = "2500k") -> List[str]:
        if self.video_source.startswith("http://") or self.video_source.startswith("https://"):
            video_input = self.video_source
            video_format = "mjpeg" if ".mjpeg" in self.video_source else "mpegts"
            video_args = ["-f", video_format, "-i", video_input]
        else:
            video_args = ["-f", "lavfi", "-i", "color=c=black:s=%dx%d" % (width, height)]

        if self.audio_source and (self.audio_source.startswith("http://") or self.audio_source.startswith("https://")):
            audio_args = [
                "-f",
                "s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-i",
                self.audio_source,
            ]
        elif self.audio_source == "silence":
            audio_args = ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        else:
            audio_args = ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]

        command = [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-loglevel",
            "warning",
            "-y",
        ]
        command += video_args
        command += audio_args
        command += [
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-b:v",
            bitrate,
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-r",
            str(fps),
            "-f",
            "mp4",
            self.output_target,
        ]
        return command


if __name__ == "__main__":
    builder = MediaPipelineBuilder(
        video_source="http://192.168.1.42:8765/camera.mjpeg?token=ABC123",
        audio_source="http://192.168.1.42:8765/audio.pcm?token=ABC123",
        output_target="demo.mp4",
    )
    print(builder.build())
