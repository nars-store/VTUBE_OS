"""Original VTUBE 2D avatar and live-overlay rendering helpers.

This module provides a more polished anime VTuber character system with a
layered vector-art look and 3D-ready metadata for future rigging workflows.
"""
import html
import re
from urllib.parse import urlsplit


TEMPLATES = {
    "Luna": {
        "hair_color": "#8C70E8",
        "eye_color": "#5545A8",
        "skin_color": "#F3C9B8",
        "outfit_color": "#5C4B9A",
        "accent_color": "#FFB454",
        "outfit": "Hoodie",
        "hair_style": "Long",
        "character_type": "idol",
    },
    "Nova": {
        "hair_color": "#E58B55",
        "eye_color": "#4C91A8",
        "skin_color": "#F1C4A5",
        "outfit_color": "#267B88",
        "accent_color": "#7EE0D7",
        "outfit": "Jacket",
        "hair_style": "Short",
        "character_type": "streamer",
    },
    "Kiro": {
        "hair_color": "#3D465F",
        "eye_color": "#B875D1",
        "skin_color": "#EFC7B1",
        "outfit_color": "#465477",
        "accent_color": "#FF8AA5",
        "outfit": "Streetwear",
        "hair_style": "Side",
        "character_type": "cyber",
    },
    "Aoi": {
        "hair_color": "#4D6CFF",
        "eye_color": "#6DD9FF",
        "skin_color": "#F8D4BF",
        "outfit_color": "#3B4D9A",
        "accent_color": "#FFD166",
        "outfit": "School Uniform",
        "hair_style": "Long",
        "character_type": "idol",
    },
    "Mika": {
        "hair_color": "#F8B5BE",
        "eye_color": "#6155C8",
        "skin_color": "#F2C4AC",
        "outfit_color": "#B44E73",
        "accent_color": "#FFB6C1",
        "outfit": "Fantasy",
        "hair_style": "Twin tails",
        "character_type": "magic",
    },
    "Yuzu": {
        "hair_color": "#0F766E",
        "eye_color": "#D3F36B",
        "skin_color": "#F5CDB8",
        "outfit_color": "#2F6F6A",
        "accent_color": "#60A5FA",
        "outfit": "Formal",
        "hair_style": "Short",
        "character_type": "host",
    },
}

OUTFITS = ("Hoodie", "Jacket", "Streetwear", "Fantasy", "Formal", "School Uniform")
HAIR_STYLES = ("Long", "Short", "Side", "Twin tails")
EXPRESSIONS = ("Smile", "Neutral", "Surprised")
COLOR_FIELDS = ("hair_color", "eye_color", "skin_color", "outfit_color", "accent_color")


def list_templates():
    """Return the available VTuber templates."""
    return list(TEMPLATES.keys())


def new_character(template="Luna", name=None):
    template = template if template in TEMPLATES else "Luna"
    entry = dict(TEMPLATES[template])
    return {
        "name": name or template,
        "template": template,
        **entry,
        "expression": "Smile",
    }


def _color(character, field, fallback):
    value = str(character.get(field, fallback))
    return value.upper() if re.fullmatch(r"#[0-9A-Fa-f]{6}", value) else fallback


def render_avatar_svg(character):
    """Return a polished anime-inspired VTuber bust illustration."""
    hair = _color(character, "hair_color", "#8C70E8")
    eye = _color(character, "eye_color", "#5545A8")
    skin = _color(character, "skin_color", "#F3C9B8")
    outfit = _color(character, "outfit_color", "#5C4B9A")
    accent = _color(character, "accent_color", "#FFB454")
    style = character.get("hair_style", "Long")
    clothes = character.get("outfit", "Hoodie")
    expression = character.get("expression", "Smile")
    name = html.escape(str(character.get("name", "VTUBE Avatar")))

    back_hair = (
        '<path d="M92 180 Q72 72 196 58 Q324 61 307 194 L292 329 '
        'Q263 361 242 304 L120 315 Q95 280 92 180Z" fill="{hair}"/>'
    ).format(hair=hair)
    if style == "Short":
        back_hair = f'<path d="M92 182 Q75 72 196 58 Q322 64 307 184 L286 254 L108 247Z" fill="{hair}"/>'
    elif style == "Side":
        back_hair = f'<path d="M90 184 Q77 68 197 58 Q326 62 308 190 L281 306 Q260 328 243 275 L119 300Z" fill="{hair}"/>'
    elif style == "Twin tails":
        back_hair = (
            f'<path d="M96 174 Q74 72 196 58 Q322 61 306 182 L291 285 L112 285Z" fill="{hair}"/>'
            f'<path d="M108 153 Q42 183 61 305 Q91 291 121 242Z" fill="{hair}"/>'
            f'<path d="M286 151 Q350 180 331 304 Q300 291 274 241Z" fill="{hair}"/>'
        )

    if clothes == "Formal":
        clothes_detail = (
            '<path d="M173 347 L200 379 L227 347 L247 495 L153 495Z" fill="#F3F0F7"/>'
            '<path d="M200 381 L215 398 L205 420 L200 416 L195 420 L185 398Z" fill="#D75D78"/>'
        )
    elif clothes == "Fantasy":
        clothes_detail = (
            '<path d="M200 350 L235 384 L213 408 L200 393 L187 408 L165 384Z" fill="#E9C66D"/>'
            '<path d="M165 420 L235 420" stroke="#E9C66D" stroke-width="8"/>'
        )
    elif clothes == "Jacket":
        clothes_detail = (
            '<path d="M200 360 L200 500" stroke="#D8E6EA" stroke-width="7"/>'
            '<path d="M154 390 L178 408 M246 390 L222 408" stroke="#D8E6EA" stroke-width="7"/>'
        )
    elif clothes == "Streetwear":
        clothes_detail = (
            '<path d="M171 360 Q200 403 229 360" fill="none" stroke="#D7DCEF" stroke-width="8"/>'
            '<path d="M174 435 L226 435" stroke="#D7DCEF" stroke-width="5"/>'
        )
    elif clothes == "School Uniform":
        clothes_detail = (
            '<path d="M145 365 L200 330 L255 365 L250 500 L150 500Z" fill="{outfit}" opacity="0.9"/>'
            '<path d="M175 330 L200 290 L225 330" fill="none" stroke="{accent}" stroke-width="7"/>'
            '<path d="M175 440 L225 440" stroke="#F8F8FF" stroke-width="6"/>'
        ).format(outfit=outfit, accent=accent)
    else:
        clothes_detail = (
            '<path d="M174 365 Q200 405 226 365" fill="none" stroke="#C9C0E8" stroke-width="8"/>'
            '<path d="M173 438 Q200 458 227 438" fill="none" stroke="#C9C0E8" stroke-width="5"/>'
        )

    mouth = {
        "Smile": '<path d="M181 251 Q200 270 219 251" fill="none" stroke="#9D5366" stroke-width="5" stroke-linecap="round"/>',
        "Neutral": '<path d="M184 258 L216 258" fill="none" stroke="#9D5366" stroke-width="5" stroke-linecap="round"/>',
        "Surprised": '<ellipse cx="200" cy="260" rx="8" ry="12" fill="#9D5366"/>',
    }.get(expression, "")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">
  <defs>
    <linearGradient id="shirtGrad" x1="0" x2="1">
      <stop offset="0%" stop-color="{outfit}" />
      <stop offset="100%" stop-color="#1E1B36" />
    </linearGradient>
    <linearGradient id="hairGrad" x1="0" x2="1">
      <stop offset="0%" stop-color="{hair}" />
      <stop offset="100%" stop-color="#1F243A" />
    </linearGradient>
    <linearGradient id="skinGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#FCE7D8" />
      <stop offset="100%" stop-color="{skin}" />
    </linearGradient>
  </defs>
  <g stroke="#332B42" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
    <path d="M142 325 Q102 340 91 405 L75 505 Q72 529 95 532 L145 522 L153 389Z" fill="url(#skinGrad)"/>
    <path d="M258 325 Q298 340 309 405 L325 505 Q328 529 305 532 L255 522 L247 389Z" fill="url(#skinGrad)"/>
    <path d="M125 356 Q200 320 275 356 L307 531 Q200 572 93 531Z" fill="url(#shirtGrad)"/>
    {clothes_detail}
    {back_hair}
    <ellipse cx="200" cy="192" rx="103" ry="126" fill="url(#skinGrad)"/>
    <path d="M102 183 Q104 74 199 68 Q288 70 300 164 Q262 133 246 105 Q206 150 112 158Z" fill="url(#hairGrad)"/>
    <path d="M110 158 Q150 153 180 126 Q168 164 141 180Z" fill="url(#hairGrad)"/>
    <path d="M194 132 Q235 149 282 148 Q261 171 224 167Z" fill="url(#hairGrad)"/>
    <ellipse cx="158" cy="201" rx="13" ry="20" fill="#FFF"/><ellipse cx="242" cy="201" rx="13" ry="20" fill="#FFF"/>
    <ellipse cx="160" cy="205" rx="7" ry="13" fill="{eye}"/><ellipse cx="240" cy="205" rx="7" ry="13" fill="{eye}"/>
    <circle cx="162" cy="201" r="3" fill="#FFF" stroke="none"/><circle cx="242" cy="201" r="3" fill="#FFF" stroke="none"/>
    <path d="M139 174 Q158 164 177 174 M223 174 Q242 164 261 174" fill="none"/>
    <path d="M198 210 L193 232 L202 234" fill="none" stroke="{skin}"/>
    {mouth}
    <ellipse cx="132" cy="237" rx="17" ry="8" fill="#E98991" opacity=".45" stroke="none"/>
    <ellipse cx="268" cy="237" rx="17" ry="8" fill="#E98991" opacity=".45" stroke="none"/>
    <circle cx="120" cy="324" r="9" fill="{accent}" opacity="0.65"/>
    <circle cx="280" cy="324" r="9" fill="{accent}" opacity="0.65"/>
  </g>
  <text x="200" y="588" text-anchor="middle" fill="#FFFFFF" stroke="none" font-family="sans-serif" font-size="18" font-weight="700">{name}</text>
</svg>'''


def render_stream_overlay_svg(character, goal, donation_link="", qr_data_uri=""):
    """Create a glossy VTuber stream overlay with goal panel and donation info."""
    avatar = render_avatar_svg(character)
    avatar_body = avatar.split(">", 1)[1].rsplit("</svg>", 1)[0]
    parsed_link = urlsplit(donation_link)
    safe_link = html.escape(donation_link, quote=True) if parsed_link.scheme in ("http", "https") and parsed_link.netloc else ""
    goal_text = html.escape(f"GOAL Rp {max(1, int(goal)):,}".replace(",", "."))
    link_text = html.escape(safe_link)
    qr_image = ""
    if qr_data_uri.startswith(("data:image/png;base64,", "data:image/jpeg;base64,")):
        qr_image = f'<image x="1650" y="130" width="210" height="210" preserveAspectRatio="xMidYMid meet" href="{qr_data_uri}"/>'
    link_svg = f'<text x="1460" y="405">{link_text}</text>' if safe_link else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <defs>
    <linearGradient id="bgGrad" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#101826"/>
      <stop offset="100%" stop-color="#1F174A"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0" x2="1">
      <stop offset="0%" stop-color="#1A233B"/>
      <stop offset="100%" stop-color="#141827"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="url(#bgGrad)"/>
  <g transform="translate(35 480) scale(.92)">{avatar_body}</g>
  <rect x="1410" y="65" width="465" height="385" rx="26" fill="url(#cardGrad)" fill-opacity="0.92" stroke="#9B7BFF" stroke-width="5"/>
  <text x="1450" y="125" font-size="35" font-weight="700" fill="#FFFFFF">{goal_text}</text>
  <text x="1450" y="170" font-size="22" fill="#D9D5FF">Vtuber donation goal</text>
  {qr_image}
  <text x="1450" y="375" font-size="23" fill="#FFFFFF">Saweria</text>
  {link_svg}
</svg>'''


if __name__ == "__main__":
    print(list_templates())
    print(render_avatar_svg(new_character("Aoi", "Aoi Live"))[:120])
    print(render_stream_overlay_svg(new_character("Mika", "Mika"), 250000, "https://saweria.co/vtube").splitlines()[0])
