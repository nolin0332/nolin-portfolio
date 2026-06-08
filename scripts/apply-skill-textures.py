#!/usr/bin/env python3
"""Apply user-provided skill logos to portfolio card textures."""
from __future__ import annotations

import json
import math
import random
import shutil
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
MANIFEST_PATH = ROOT / "scripts" / "logo-manifest.json"
CURSOR_ASSETS = Path(
    r"C:\Users\Admin\.cursor\projects\d-Program-All-Portfolio-TimothyCalderPortfolio\assets"
)
LOGOS_OUT = PUBLIC / "assets" / "logos"

LEADERBOARD_SIZE = 160
LEADERBOARD_WHITE_BG = frozenset({"python", "pytorch", "aws", "rag", "azure-ai"})
QUEST_1_SIZE = (520, 720)
QUEST_23_SIZE = (560, 788)
QUEST_LOGO_PAD = {
    "azure-ai": 0.008,
    "pytorch": 0.006,
    "azure": 0.02,
}
JOB_SIZE = (640, 860)
TOOL_SIZE = (272, 144)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def resolve_source(name: str, logos: dict[str, str]) -> Path:
    suffix = logos[name]
    for base in (LOGOS_OUT, CURSOR_ASSETS):
        if not base.exists():
            continue
        if base == LOGOS_OUT:
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate = base / f"{name}{ext}"
                if candidate.exists():
                    return candidate
        matches = list(base.glob(f"*{suffix}"))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"Logo source not found for {name}")


def install_logos(logos: dict[str, str]) -> dict[str, Path]:
    LOGOS_OUT.mkdir(parents=True, exist_ok=True)
    installed: dict[str, Path] = {}
    for key, _suffix in logos.items():
        src = resolve_source(key, logos)
        dest = LOGOS_OUT / f"{key}{src.suffix.lower()}"
        try:
            shutil.copy2(src, dest)
        except PermissionError:
            if dest.exists():
                print(f"  kept existing logo {key} (file locked)")
            else:
                raise
        else:
            print(f"  installed logo {key} <- {src.name}")
        installed[key] = dest
    return installed


def strip_near_white(img: "Image.Image", threshold: int = 245) -> "Image.Image":
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                px[x, y] = (r, g, b, 0)
    return img


def flatten_logo_on_white(logo: "Image.Image", threshold: int = 220) -> "Image.Image":
    from PIL import Image

    logo = logo.convert("RGBA")
    flattened = strip_near_white(logo.copy(), threshold=threshold)
    canvas = Image.new("RGBA", logo.size, (255, 255, 255, 255))
    canvas.paste(flattened, (0, 0), flattened)
    return canvas


def flatten_logo_for_white_card(logo: "Image.Image") -> "Image.Image":
    from PIL import Image

    logo = logo.convert("RGBA")
    px = logo.load()
    w, h = logo.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            mx = max(r, g, b)
            mn = min(r, g, b)
            if r >= 220 and g >= 220 and b >= 220:
                px[x, y] = (r, g, b, 0)
            elif mx < 55 and (mx - mn) < 35:
                px[x, y] = (r, g, b, 0)
    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    canvas.paste(logo, (0, 0), logo)
    return canvas


def flatten_rag_logo_on_white(logo: "Image.Image") -> "Image.Image":
    from PIL import Image

    logo = flatten_logo_on_white(logo.copy())
    px = logo.load()
    w, h = logo.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 64 and max(r, g, b) < 200:
                px[x, y] = (0, 0, 0, 255)
    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    canvas.paste(logo, (0, 0), logo)
    return canvas


def flatten_logo_for_quest_inset(logo_key: str, logo: "Image.Image") -> "Image.Image":
    if logo_key == "rag":
        return flatten_rag_logo_on_white(logo)
    if logo_key in ("aws", "aws-mlops"):
        return flatten_logo_for_white_card(logo)
    return flatten_logo_on_white(logo)


def fit_contain(
    logo: "Image.Image", box_w: int, box_h: int, pad: float = 0.04
) -> "Image.Image":
    from PIL import Image

    inner_w = max(1, int(box_w * (1 - pad * 2)))
    inner_h = max(1, int(box_h * (1 - pad * 2)))
    fitted = logo.copy()
    fitted.thumbnail((inner_w, inner_h), Image.Resampling.LANCZOS)
    return fitted


def radial_portrait_bg(
    width: int, height: int, color: str | None
) -> "Image.Image":
    from PIL import Image

    if not color:
        top = (18, 22, 32)
    else:
        top = hex_to_rgb(color)
    bottom = tuple(max(0, c - 72) for c in top)
    edge = tuple(max(0, c - 110) for c in top)
    bg = Image.new("RGBA", (width, height))
    px = bg.load()
    cx, cy = width * 0.5, height * 0.34
    max_dist = (width * width + height * height) ** 0.5 * 0.55
    for y in range(height):
        for x in range(width):
            t_y = y / max(height - 1, 1)
            base = tuple(
                int(top[i] * (1 - t_y) + bottom[i] * t_y) for i in range(3)
            )
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            vignette = min(1.0, dist / max_dist)
            row = tuple(
                int(base[i] * (1 - vignette * 0.55) + edge[i] * (vignette * 0.55))
                for i in range(3)
            )
            px[x, y] = row + (255,)
    return bg


def draw_accent_line(canvas: "Image.Image", color: str | None) -> None:
    from PIL import ImageDraw

    if not color:
        accent = (80, 180, 220, 255)
    else:
        rgb = hex_to_rgb(color)
        accent = tuple(min(255, c + 70) for c in rgb) + (255,)
    w, h = canvas.size
    draw = ImageDraw.Draw(canvas)
    y = int(h * 0.72)
    line_w = int(w * 0.34)
    x0 = (w - line_w) // 2
    draw.line((x0, y, x0 + line_w, y), fill=accent, width=max(2, w // 180))


def _accent_colors(bg_color: str | None) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    if not bg_color:
        base = (18, 22, 32)
    else:
        base = hex_to_rgb(bg_color)
    bright = tuple(min(255, c + 95) for c in base)
    soft = tuple(min(255, int(c * 0.55 + 80)) for c in base)
    return base, bright, soft


def _add_glow(
    canvas: "Image.Image",
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int],
    alpha: int,
    blur: int,
) -> "Image.Image":
    from PIL import Image, ImageDraw, ImageFilter

    w, h = canvas.size
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=color + (alpha,),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(4, blur)))
    return Image.alpha_composite(canvas, glow)


def _shade_bottom_band(canvas: "Image.Image", start: float = 0.68) -> "Image.Image":
    from PIL import Image, ImageDraw

    w, h = canvas.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    y0 = int(h * start)
    for y in range(y0, h):
        t = (y - y0) / max(h - y0, 1)
        draw.line((0, y, w, y), fill=(0, 0, 0, int(55 * t)))
    return Image.alpha_composite(canvas, overlay)


def _draw_forecast_curve(
    draw: "ImageDraw.ImageDraw",
    width: int,
    height: int,
    y_center: int,
    amplitude: int,
    color: tuple[int, int, int, int],
    width_px: int,
) -> None:
    points = []
    x0 = int(width * 0.12)
    x1 = int(width * 0.88)
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(x1 - x0, 1)
        wave = math.sin(t * math.pi * 2.4) * 0.55 + math.sin(t * math.pi * 5.2 + 0.8) * 0.25
        y = y_center + int(wave * amplitude)
        points.append((x, y))
    for i in range(len(points) - 1):
        draw.line((points[i], points[i + 1]), fill=color, width=width_px)


def _draw_job_motif(
    canvas: "Image.Image",
    job: str,
    bright: tuple[int, int, int],
    soft: tuple[int, int, int],
) -> None:
    from PIL import ImageDraw

    w, h = canvas.size
    draw = ImageDraw.Draw(canvas)
    cx, cy = w // 2, int(h * 0.30)
    unit = min(w, h)

    if job == "healthcare-rag":
        for i, offset in enumerate((-int(unit * 0.12), 0, int(unit * 0.12))):
            alpha = 70 + i * 25
            draw.rounded_rectangle(
                (
                    cx + offset - int(unit * 0.18),
                    cy - int(unit * 0.16),
                    cx + offset + int(unit * 0.18),
                    cy + int(unit * 0.16),
                ),
                radius=int(unit * 0.03),
                outline=bright + (alpha,),
                width=max(2, w // 220),
            )
        nodes = [
            (cx - int(unit * 0.2), cy - int(unit * 0.04)),
            (cx, cy - int(unit * 0.14)),
            (cx + int(unit * 0.2), cy - int(unit * 0.04)),
            (cx, cy + int(unit * 0.12)),
        ]
        for a, b in ((0, 1), (1, 2), (1, 3), (0, 3), (2, 3)):
            draw.line((nodes[a], nodes[b]), fill=soft + (90,), width=max(2, w // 260))
        for x, y in nodes:
            r = int(unit * 0.022)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 180))
        r = int(unit * 0.28)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=bright + (45,), width=max(2, w // 240))

    elif job == "energy-ml":
        sun_y = cy - int(unit * 0.18)
        sun_r = int(unit * 0.1)
        draw.ellipse(
            (cx - sun_r, sun_y - sun_r, cx + sun_r, sun_y + sun_r),
            fill=(255, 220, 120, 200),
        )
        for i in range(8):
            ang = math.pi * 2 * i / 8
            x0 = cx + int(math.cos(ang) * sun_r * 1.2)
            y0 = sun_y + int(math.sin(ang) * sun_r * 1.2)
            x1 = cx + int(math.cos(ang) * sun_r * 1.75)
            y1 = sun_y + int(math.sin(ang) * sun_r * 1.75)
            draw.line((x0, y0, x1, y1), fill=(255, 230, 150, 140), width=max(2, w // 280))

        hub_x, hub_y = cx - int(unit * 0.08), cy + int(unit * 0.06)
        pole_top = hub_y + int(unit * 0.16)
        draw.line((hub_x, hub_y, hub_x, pole_top), fill=bright + (120,), width=max(3, w // 200))
        for angle_deg in (0, 120, 240):
            ang = math.radians(angle_deg - 90)
            blade = int(unit * 0.2)
            x1 = hub_x + int(math.cos(ang) * blade)
            y1 = hub_y + int(math.sin(ang) * blade)
            draw.line((hub_x, hub_y, x1, y1), fill=(255, 255, 255, 170), width=max(3, w // 180))

        _draw_forecast_curve(
            draw,
            w,
            h,
            cy + int(unit * 0.14),
            int(unit * 0.08),
            (255, 255, 255, 170),
            max(2, w // 200),
        )
        for i in range(6):
            bx = int(w * 0.18) + int((w * 0.64) * i / 5)
            bh = int(unit * 0.03) + i % 3 * int(unit * 0.015)
            draw.rectangle(
                (bx - int(unit * 0.012), cy + int(unit * 0.22) - bh, bx + int(unit * 0.012), cy + int(unit * 0.22)),
                fill=bright + (130,),
            )

    elif job == "grid-forecasting":
        grid_top = cy - int(unit * 0.2)
        grid_bottom = cy + int(unit * 0.18)
        grid_left = int(w * 0.18)
        grid_right = int(w * 0.82)
        for i in range(7):
            x = grid_left + int((grid_right - grid_left) * i / 6)
            draw.line((x, grid_top, x, grid_bottom), fill=soft + (55,), width=1)
        for i in range(6):
            y = grid_top + int((grid_bottom - grid_top) * i / 5)
            draw.line((grid_left, y, grid_right, y), fill=soft + (55,), width=1)

        sweep_r = int(unit * 0.24)
        draw.pieslice(
            (cx - sweep_r, cy - sweep_r, cx + sweep_r, cy + sweep_r),
            start=300,
            end=20,
            fill=bright + (75,),
        )
        _draw_forecast_curve(
            draw,
            w,
            h,
            cy + int(unit * 0.02),
            int(unit * 0.06),
            (255, 255, 255, 150),
            max(2, w // 220),
        )
        for i in range(4):
            px = grid_left + int((grid_right - grid_left) * (0.15 + i * 0.22))
            draw.ellipse(
                (px - int(unit * 0.018), grid_bottom + int(unit * 0.03), px + int(unit * 0.018), grid_bottom + int(unit * 0.07)),
                fill=bright + (110,),
            )
    else:
        r = int(unit * 0.24)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=bright + (80,), width=max(2, w // 200))


def make_abstract_job_card(
    job: str,
    width: int,
    height: int,
    bg_color: str | None,
) -> bytes:
    from PIL import ImageDraw

    canvas = radial_portrait_bg(width, height, bg_color)
    _, bright, soft = _accent_colors(bg_color)
    cx, cy = width // 2, int(height * 0.30)
    unit = min(width, height)

    canvas = _add_glow(canvas, cx, cy, int(unit * 0.44), bright, 50, unit // 14)
    canvas = _add_glow(canvas, cx, cy, int(unit * 0.16), (255, 255, 255), 22, unit // 18)

    _draw_job_motif(canvas, job, bright, soft)

    draw = ImageDraw.Draw(canvas)
    rng = random.Random(f"job-{job}-{width}x{height}")
    for _ in range(22):
        x = rng.randint(int(width * 0.1), int(width * 0.9))
        y = rng.randint(int(height * 0.08), int(height * 0.56))
        r = rng.randint(1, max(2, width // 300))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=bright + (rng.randint(16, 42),))

    draw_accent_line(canvas, bg_color)
    canvas = _shade_bottom_band(canvas)

    out = BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def paste_centered(
    canvas: "Image.Image",
    logo: "Image.Image",
    box: tuple[int, int, int, int],
    pad: float = 0.04,
) -> None:
    x0, y0, x1, y1 = box
    box_w, box_h = x1 - x0, y1 - y0
    fitted = fit_contain(logo, box_w, box_h, pad=pad)
    x = x0 + (box_w - fitted.width) // 2
    y = y0 + (box_h - fitted.height) // 2
    canvas.paste(fitted, (x, y), fitted)


def make_leaderboard_texture(
    logo_path: Path,
    bg_color: str | None,
    strip_white: bool,
    *,
    force_white_bg: bool = False,
    logo_key: str | None = None,
) -> bytes:
    from PIL import Image

    size = LEADERBOARD_SIZE
    if force_white_bg:
        canvas_bg = (255, 255, 255)
        strip_white = False
    elif bg_color:
        rgb = hex_to_rgb(bg_color)
        canvas_bg = tuple(max(0, c - 40) for c in rgb)
    else:
        canvas_bg = (14, 18, 28)
    canvas = Image.new("RGBA", (size, size), canvas_bg + (255,))

    logo = Image.open(logo_path).convert("RGBA")
    if force_white_bg:
        logo = flatten_logo_for_quest_inset(logo_key or logo_path.stem, logo)
    elif strip_white:
        logo = strip_near_white(logo)

    inset = int(size * 0.04)
    lb_pad = (
        0.0
        if logo_key in ("azure-ai", "pytorch")
        else (0.01 if not force_white_bg else 0.0)
    )
    paste_centered(
        canvas,
        logo,
        (inset, inset, size - inset, size - inset),
        pad=lb_pad,
    )

    out = BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def make_portrait_card_texture(
    logo_path: Path,
    width: int,
    height: int,
    bg_color: str | None,
    strip_white: bool,
    *,
    logo_white_bg: bool = False,
    logo_key: str | None = None,
) -> bytes:
    from PIL import Image, ImageDraw

    canvas = radial_portrait_bg(width, height, bg_color)
    box = (
        int(width * 0.06),
        int(height * 0.06),
        int(width * 0.94),
        int(height * 0.58),
    )

    if logo_white_bg:
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle(
            box,
            radius=int(min(width, height) * 0.04),
            fill=(255, 255, 255, 255),
        )
        logo = flatten_logo_for_quest_inset(
            logo_key or logo_path.stem,
            Image.open(logo_path),
        )
    else:
        logo = Image.open(logo_path).convert("RGBA")
        if strip_white:
            logo = strip_near_white(logo)

    logo_pad = QUEST_LOGO_PAD.get(logo_key or logo_path.stem, 0.02 if logo_white_bg else 0.03)
    paste_centered(canvas, logo, box, pad=logo_pad)
    draw_accent_line(canvas, bg_color)

    out = BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def make_tool_card_texture(
    logo_path: Path,
    bg_color: str | None,
    strip_white: bool,
    *,
    force_white_bg: bool = False,
) -> bytes:
    from PIL import Image, ImageDraw

    width, height = TOOL_SIZE
    if force_white_bg:
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        logo = flatten_logo_for_white_card(Image.open(logo_path))
        pad = 0.02
        border = (210, 214, 220, 200)
    else:
        canvas = radial_portrait_bg(width, height, bg_color)
        logo = Image.open(logo_path).convert("RGBA")
        if strip_white:
            logo = strip_near_white(logo)
        pad = 0.04
        border = (255, 255, 255, 40)

    paste_centered(canvas, logo, (8, 8, width - 8, height - 8), pad=pad)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=10,
        outline=border,
        width=1,
    )

    out = BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def save_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"  wrote {path.relative_to(PUBLIC)}")


def color_for_logo(name: str, profile: dict) -> str | None:
    for group in ("quests_cards", "jobs", "tools"):
        for card in profile.get(group, {}).get("cards", []):
            logo_key = card.get("logo") or card.get("icon", "").replace(
                "amazonwebservices", "aws"
            )
            if (
                logo_key == name
                or card.get("label", "").lower().replace(" / ", "-").replace(" ", "-")
                == name
            ):
                return card.get("color")
    defaults = {
        "python": "#3776AB",
        "rag": "#2A2A2A",
        "pytorch": "#EE4C2C",
        "aws": "#232F3E",
        "aws-mlops": "#232F3E",
        "azure": "#0078D4",
        "azure-ai": "#0078D4",
        "langchain": "#1C3C3C",
        "healthcare-rag": "#00796B",
        "energy-ml": "#FF6F00",
        "grid-forecasting": "#455A64",
    }
    return defaults.get(name)


def main() -> None:
    from PIL import Image

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    profile = json.loads((ROOT / "scripts" / "resume-profile.json").read_text(encoding="utf-8"))

    print("Installing source logos...")
    installed = install_logos(manifest["logos"])

    print("Building textures...")
    for filename, logo_key in manifest["textures"]["leaderboard"].items():
        data = make_leaderboard_texture(
            installed[logo_key],
            bg_color=color_for_logo(logo_key, profile),
            strip_white=logo_key not in ("aws", "aws-mlops", "pytorch", "azure-ai"),
            force_white_bg=logo_key in LEADERBOARD_WHITE_BG,
            logo_key=logo_key,
        )
        save_bytes(PUBLIC / "assets" / "images" / "leaderboard" / filename, data)

    quest_sizes = {
        "quest_1_card_1.png": QUEST_1_SIZE,
        "quest_1_card_2.png": QUEST_1_SIZE,
        "quest_1_card_3.png": QUEST_1_SIZE,
        "quest_2_card.png": QUEST_23_SIZE,
        "quest_3_card.png": QUEST_23_SIZE,
    }
    for filename, logo_key in manifest["textures"]["quests"].items():
        w, h = quest_sizes[filename]
        data = make_portrait_card_texture(
            installed[logo_key],
            w,
            h,
            bg_color=color_for_logo(logo_key, profile),
            strip_white=logo_key not in ("aws", "azure-ai", "pytorch", "aws-mlops"),
            logo_white_bg=True,
            logo_key=logo_key,
        )
        save_bytes(PUBLIC / "assets" / "textures" / "gamificationQuests" / filename, data)

    w, h = JOB_SIZE
    for filename, logo_key in manifest["textures"]["jobs"].items():
        data = make_abstract_job_card(
            logo_key,
            w,
            h,
            bg_color=color_for_logo(logo_key, profile),
        )
        save_bytes(PUBLIC / "assets" / "textures" / "storyRewardsCashback" / filename, data)

    for filename, logo_key in manifest["textures"]["tools"].items():
        png_data = make_tool_card_texture(
            installed[logo_key],
            bg_color=color_for_logo(logo_key, profile),
            strip_white=logo_key not in ("aws",),
            force_white_bg=True,
        )
        out = PUBLIC / "assets" / "textures" / "storyAirdropPreEngagement" / filename
        out.parent.mkdir(parents=True, exist_ok=True)
        img = Image.open(BytesIO(png_data)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=92)
        out.write_bytes(buf.getvalue())
        print(f"  wrote {out.relative_to(PUBLIC)}")

    print("Done.")


if __name__ == "__main__":
    main()
