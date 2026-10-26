#!/usr/bin/env python3
"""Generate the social-share cover image (public/assets/meta/cover.png)
from scripts/resume-profile.json, matching the site's dark/orange look."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "scripts" / "resume-profile.json"
OUT = ROOT / "public" / "assets" / "meta" / "cover.png"
FONTS = ROOT / "public" / "assets" / "fonts"

W, H = 1200, 630
SCALE = 2  # render at 2x then downsample for crisp text


def font(name: str, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS / name), size * SCALE)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def background() -> Image.Image:
    w, h = W * SCALE, H * SCALE
    img = Image.new("RGB", (w, h), (10, 8, 16))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse((-w * 0.25, h * 0.15, w * 0.45, h * 1.15), fill=(92, 42, 20))
    d.ellipse((w * 0.55, -h * 0.5, w * 1.25, h * 0.45), fill=(36, 22, 48))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=220 * SCALE / 2))
    return Image.blend(img, Image.composite(glow, img, glow.convert("L").point(lambda v: min(255, v * 3))), 0.75)


def gradient_text(base: Image.Image, xy: tuple[int, int], text: str, f: ImageFont.FreeTypeFont,
                  c0: tuple[int, int, int], c1: tuple[int, int, int]) -> int:
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, fill=255)
    bbox = mask.getbbox()
    grad = Image.new("RGB", base.size, c0)
    gd = ImageDraw.Draw(grad)
    x0, x1 = bbox[0], bbox[2]
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(1, x1 - x0)
        col = tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3))
        gd.line((x, bbox[1], x, bbox[3]), fill=col)
    base.paste(grad, (0, 0), mask)
    return bbox[3]


def main() -> None:
    p = json.loads(PROFILE.read_text(encoding="utf-8"))["profile"]
    name = p["name"]
    title = p["title"].upper()
    tagline = p["tagline"]
    linkedin = re.sub(r"^https?://(www\.)?", "", p["linkedin"]).rstrip("/")

    img = background()
    draw = ImageDraw.Draw(img)
    s = SCALE
    x = 92 * s

    # accent bar
    draw.rounded_rectangle((x, 206 * s, x + 64 * s, 211 * s), radius=3 * s, fill=(255, 190, 120))

    # name with warm gradient
    gradient_text(img, (x, 236 * s), name, font("GolosText-Variable.ttf", 76, 800),
                  (255, 244, 230), (255, 160, 70))

    # role
    role_font = font("GolosText-Variable.ttf", 26, 700)
    rx = x
    for ch in title:  # manual letter-spacing
        draw.text((rx, 352 * s), ch, font=role_font, fill=(255, 150, 70))
        rx += draw.textlength(ch, font=role_font) + 5 * s

    # tagline, wrapped to two lines max
    tag_font = font("GolosText-Variable.ttf", 24, 450)
    words = tagline.split()
    lines, cur = [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if draw.textlength(test, font=tag_font) > (W - 184) * s:
            lines.append(cur)
            cur = w_
        else:
            cur = test
        if len(lines) == 2:
            break
    if len(lines) < 2 and cur:
        lines.append(cur)
    if len(lines) == 2 and len(" ".join(lines)) < len(tagline):
        lines[1] = lines[1].rstrip(" ,.;:") + "…"
    y = 430 * s
    for ln in lines:
        draw.text((x, y), ln, font=tag_font, fill=(228, 220, 214))
        y += 40 * s

    # linkedin
    draw.text((x, 560 * s), linkedin, font=font("GolosText-Variable.ttf", 20, 600), fill=(150, 142, 140))

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"Wrote {OUT.relative_to(ROOT)} ({W}x{H})")


if __name__ == "__main__":
    main()
