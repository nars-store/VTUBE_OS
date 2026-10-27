import unittest
import xml.etree.ElementTree as ET

from vtube_avatar import new_character, render_avatar_svg, render_stream_overlay_svg


class AvatarRenderingTests(unittest.TestCase):
    def test_templates_render_valid_svg_with_customizable_features(self):
        character = new_character("Nova", "Nova & Friends")
        character.update({
            "hair_color": "#123456",
            "eye_color": "#ABCDEF",
            "outfit_color": "#654321",
            "outfit": "Formal",
            "expression": "Surprised",
        })

        svg = render_avatar_svg(character)
        root = ET.fromstring(svg)

        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("#123456", svg)
        self.assertIn("#ABCDEF", svg)
        self.assertIn("Nova &amp; Friends", svg)
        self.assertIn('<ellipse cx="200" cy="260" rx="8" ry="12"', svg)

    def test_invalid_color_falls_back_to_template_color(self):
        character = new_character()
        character["hair_color"] = "url(javascript:alert(1))"

        self.assertIn('fill="#8C70E8"', render_avatar_svg(character))

    def test_live_overlay_contains_avatar_goal_and_donation_qr(self):
        svg = render_stream_overlay_svg(
            new_character("Kiro"),
            250000,
            "https://saweria.co/vtube",
            "data:image/png;base64,cXItZGF0YQ==",
        )
        root = ET.fromstring(svg)

        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("GOAL Rp 250.000", svg)
        self.assertIn("https://saweria.co/vtube", svg)
        self.assertIn("data:image/png;base64,cXItZGF0YQ==", svg)
        self.assertIn("Kiro", svg)


if __name__ == "__main__":
    unittest.main()
