"""VTuber original-character customization system.

This editor intentionally works with template-driven customization so creators can
build an original VTuber look without copying another artist's exact design.
It keeps the avatar rig structure intact while allowing color, outfit, accessory,
and expression changes to be exported as a reusable config.
"""
from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_TEMPLATE_PATH = "assets/avatars/template_avatar.json"


@dataclass
class AvatarCustomization:
    name: str = "Original VTuber"
    style: str = "idol"
    palette: Dict[str, str] = field(default_factory=lambda: {
        "skin": "#F4D0B8",
        "hair": "#6B4F9A",
        "eye": "#4C7CFF",
        "outfit_primary": "#8B5CF6",
        "outfit_secondary": "#E2D8FF",
        "accent": "#F8B4D9",
    })
    clothing: Dict[str, str] = field(default_factory=lambda: {
        "top": "idol_uniform",
        "bottom": "skirt",
        "outerwear": "jacket",
        "style": "cute_streamer",
    })
    features: Dict[str, str] = field(default_factory=lambda: {
        "eye_shape": "large_round",
        "bangs": "soft_side",
        "hair_length": "mid_long",
        "expression_default": "smile",
        "pose": "idle",
    })
    rig: Dict[str, float] = field(default_factory=lambda: {
        "head_yaw": 0.0,
        "head_pitch": 0.0,
        "head_roll": 0.0,
        "blink": 0.0,
        "smile": 0.0,
        "mouth_open": 0.0,
        "eyebrow_raise": 0.0,
    })

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "style": self.style,
            "palette": self.palette,
            "clothing": self.clothing,
            "features": self.features,
            "rig": self.rig,
        }


class AvatarTemplateEditor:
    """Edit a VTuber template while retaining the same rig structure."""

    def __init__(self, template_path: str | Path = DEFAULT_TEMPLATE_PATH):
        self.template_path = Path(template_path)
        self.template = self._load_template()

    def _load_template(self) -> Dict[str, Any]:
        if not self.template_path.exists():
            return AvatarCustomization().as_dict()
        return json.loads(self.template_path.read_text(encoding="utf-8"))

    def save(self, path: str | Path | None = None) -> str:
        target = Path(path) if path else self.template_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.template, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(target)

    def update_palette(self, **colors: str) -> Dict[str, str]:
        self.template.setdefault("palette", {})
        self.template["palette"].update(colors)
        return self.template["palette"]

    def update_clothing(self, **clothing: str) -> Dict[str, str]:
        self.template.setdefault("clothing", {})
        self.template["clothing"].update(clothing)
        return self.template["clothing"]

    def update_features(self, **features: str) -> Dict[str, str]:
        self.template.setdefault("features", {})
        self.template["features"].update(features)
        return self.template["features"]

    def update_rig(self, **rig: float) -> Dict[str, float]:
        self.template.setdefault("rig", {})
        self.template["rig"].update(rig)
        return self.template["rig"]

    def make_variant(self, name: str, style: str = "idol", **overrides: Any) -> Dict[str, Any]:
        variant = deepcopy(self.template)
        variant["name"] = name
        variant["style"] = style
        for section, values in overrides.items():
            if isinstance(values, dict):
                variant.setdefault(section, {}).update(values)
        return variant

    def export_character(self, name: str, style: str = "idol", **overrides: Any) -> Dict[str, Any]:
        return self.make_variant(name, style, **overrides)


def create_original_character(name: str = "Original VTuber", style: str = "idol", **overrides: Any) -> Dict[str, Any]:
    editor = AvatarTemplateEditor()
    return editor.export_character(name, style, **overrides)


if __name__ == "__main__":
    editor = AvatarTemplateEditor()
    custom = editor.export_character(
        "Astra",
        "cyber",
        palette={"hair": "#3B82F6", "outfit_primary": "#0F172A", "accent": "#22D3EE"},
        clothing={"top": "cyber_hoodie", "style": "streamer_look"},
        features={"bangs": "sharp", "expression_default": "confident"},
    )
    print(json.dumps(custom, indent=2, ensure_ascii=False))
