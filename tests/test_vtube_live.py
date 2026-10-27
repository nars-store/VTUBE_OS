import unittest

from vtube_live import build_stream_command, phone_stream_url, rtmp_target


class PhoneStreamUrlTests(unittest.TestCase):
    def test_builds_encoded_url_for_private_phone(self):
        self.assertEqual(
            phone_stream_url("192.168.1.25", "abc234", "screen.mjpeg"),
            "http://192.168.1.25:8765/screen.mjpeg?token=ABC234",
        )

    def test_rejects_non_lan_addresses_invalid_codes_and_unknown_endpoints(self):
        for host in ("127.0.0.1", "8.8.8.8", "169.254.1.5"):
            with self.subTest(host=host), self.assertRaises(ValueError):
                phone_stream_url(host, "ABC234", "screen.mjpeg")
        with self.assertRaises(ValueError):
            phone_stream_url("192.168.1.25", "bad!", "screen.mjpeg")
        with self.assertRaises(ValueError):
            phone_stream_url("192.168.1.25", "ABC234", "unknown")


class RtmpTargetTests(unittest.TestCase):
    def test_joins_server_and_stream_key(self):
        self.assertEqual(
            rtmp_target("rtmps://live.example.test/app/", "secret/key"),
            "rtmps://live.example.test/app/secret/key",
        )

    def test_rejects_unsafe_or_incomplete_destinations(self):
        for server, key in (
            ("https://live.example.test", "key"),
            ("rtmp://user@live.example.test/app", "key"),
            ("rtmp://live.example.test/app?x=1", "key"),
            ("rtmp://live.example.test/app", ""),
            ("rtmp://live.example.test/app", "bad key"),
        ):
            with self.subTest(server=server, key=key), self.assertRaises(ValueError):
                rtmp_target(server, key)


class StreamCommandTests(unittest.TestCase):
    def build(self, **overrides):
        options = {
            "ffmpeg": "/usr/bin/ffmpeg",
            "video_source": "phone-screen",
            "audio_source": "phone-mic",
            "target": "rtmp://live.example.test/app/key",
            "width": 1280,
            "height": 720,
            "fps": 30,
            "bitrate": "4500k",
            "overlay_png": "/tmp/vtube-overlay.png",
            "phone_host": "192.168.1.25",
            "pair_code": "ABC234",
        }
        options.update(overrides)
        return build_stream_command(**options)

    def test_composes_phone_screen_and_microphone_with_overlay(self):
        command = self.build()

        self.assertIn("http://192.168.1.25:8765/screen.mjpeg?token=ABC234", command)
        self.assertIn("http://192.168.1.25:8765/audio.pcm?token=ABC234", command)
        self.assertIn("[base][overlay]overlay=0:0:shortest=1[outv]", " ".join(command))
        self.assertIn("-c:v", command)
        self.assertIn("libx264", command)
        self.assertEqual(command[-1], "rtmp://live.example.test/app/key")

    def test_maps_audio_only_mode_and_validates_sources(self):
        command = self.build(
            video_source="desktop",
            audio_source="none",
            display=":0.0",
            target="rtmp://live.example.test/live/key",
        )

        self.assertIn("x11grab", command)
        self.assertIn("anullsrc=channel_layout=stereo:sample_rate=44100", command)
        self.assertIn("-map", command)

        with self.assertRaises(ValueError):
            self.build(video_source="unknown")
        with self.assertRaises(ValueError):
            self.build(fps=25)
        with self.assertRaises(ValueError):
            self.build(bitrate="1k")


if __name__ == "__main__":
    unittest.main()
