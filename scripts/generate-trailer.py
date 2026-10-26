#!/usr/bin/env python
"""Render the branded hero trailer videos for the portfolio.

The intro section of the site plays `public/assets/videos/test_trailer.mp4`
(muted, looping) as a WebGL video texture. This script renders a seamless,
loopable motion-graphics trailer in the site's palette from the data in
`scripts/resume-profile.json`.

Usage:
    python scripts/generate-trailer.py                 # both variants
    python scripts/generate-trailer.py landscape       # 1920x1080 only
    python scripts/generate-trailer.py portrait        # 1080x1920 only
    python scripts/generate-trailer.py landscape --preview DIR   # PNG stills only
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "public", "assets", "fonts", "GolosText-Variable.ttf")
LOGO_DIR = os.path.join(ROOT, "public", "assets", "logos")
VIDEO_DIR = os.path.join(ROOT, "public", "assets", "videos")
PROFILE = json.load(open(os.path.join(ROOT, "scripts", "resume-profile.json"), encoding="utf-8"))

FPS = 30
DURATION = 15.0  # seconds, seamless loop

ORANGE = (255, 114, 37)
LIGHT_ORANGE = (255, 219, 183)
WHITE = (239, 239, 239)

PREVIEW_TIMES = [0.9, 2.6, 5.4, 8.9, 12.2, 14.1]


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


# ----------------------------------------------------------------------------- easing
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def fit(t: float, a: float, b: float) -> float:
    return clamp01((t - a) / (b - a))


def ease_out_cubic(p: float) -> float:
    return 1 - (1 - p) ** 3


def ease_in_out(p: float) -> float:
    return p * p * (3 - 2 * p)


def ease_out_back(p: float) -> float:
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def ease_out_expo(p: float) -> float:
    return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)


# ----------------------------------------------------------------------------- drawing helpers
_FONTS: dict = {}


def F(size: float, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    key = (int(round(size)), weight)
    if key not in _FONTS:
        f = ImageFont.truetype(FONT_PATH, key[0])
        f.set_variation_by_name(weight)
        _FONTS[key] = f
    return _FONTS[key]


def with_alpha(im: Image.Image, alpha: float) -> Image.Image:
    if alpha >= 0.999:
        return im
    a = im.getchannel("A").point(lambda v: int(v * alpha))
    im = im.copy()
    im.putalpha(a)
    return im


def blit(canvas: Image.Image, layer: Image.Image, x: float, y: float) -> None:
    """Alpha-composite `layer` onto `canvas` at (x, y), cropping to the canvas."""
    x, y = int(round(x)), int(round(y))
    W, H = canvas.size
    w, h = layer.size
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (x, y, x + w, y + h):
        layer = layer.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    canvas.alpha_composite(layer, dest=(x0, y0))


def text_layer(txt: str, fnt, fill, alpha=1.0, blur=0.0, glow=None, glow_r=18, glow_a=0.55, tracking=0.0):
    """Render text to an RGBA layer. Returns (layer, ox, oy) so that pasting at
    (x + ox, y + oy) matches ImageDraw.text((x, y), anchor='la')."""
    pad = int(max(glow_r * 2 if glow else 0, blur * 3, 8)) + 6
    if tracking:
        widths = [fnt.getlength(c) for c in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        asc, desc = fnt.getmetrics()
        bbox = (0, 0, int(math.ceil(total)), asc + desc)
    else:
        bbox = fnt.getbbox(txt)
    w = bbox[2] - bbox[0] + 2 * pad
    h = bbox[3] - bbox[1] + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad - bbox[0], pad - bbox[1]
    if tracking:
        x = ox
        for c, cw in zip(txt, widths):
            d.text((x, oy), c, font=fnt, fill=tuple(fill) + (255,))
            x += cw + tracking
    else:
        d.text((ox, oy), txt, font=fnt, fill=tuple(fill) + (255,))
    if glow:
        g = Image.new("RGBA", im.size, tuple(glow) + (0,))
        g.putalpha(im.getchannel("A"))
        g = g.filter(ImageFilter.GaussianBlur(glow_r))
        g = with_alpha(g, glow_a)
        g.alpha_composite(im)
        im = g
    if blur > 0.2:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im = with_alpha(im, alpha)
    return im, -ox, -oy


def tracked_width(txt: str, fnt, tracking: float) -> float:
    return sum(fnt.getlength(c) for c in txt) + tracking * (len(txt) - 1)


def rounded_rect_layer(w, h, radius, fill, outline=None, width=2):
    im = Image.new("RGBA", (int(w) + 4, int(h) + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, int(w) + 1, int(h) + 1), radius=radius, fill=fill, outline=outline, width=width)
    return im


def scale_about_center(layer: Image.Image, s: float) -> Image.Image:
    """Scale an RGBA layer about its center, keeping its size (cropped/padded)."""
    if abs(s - 1) < 1e-3:
        return layer
    w, h = layer.size
    nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
    r = layer.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    blit(out, r, (w - nw) / 2, (h - nh) / 2)
    return out


_GLOWS: dict = {}


def glow_sprite(size: int) -> np.ndarray:
    """Soft radial falloff in [0,1], shape (size, size), float32."""
    if size not in _GLOWS:
        ax = np.linspace(-1, 1, size, dtype=np.float32)
        xx, yy = np.meshgrid(ax, ax)
        r2 = xx * xx + yy * yy
        _GLOWS[size] = np.exp(-r2 * 3.2).astype(np.float32) * (r2 < 1).astype(np.float32)
    return _GLOWS[size]


def add_glow(img: np.ndarray, cx: float, cy: float, size: int, color, strength: float) -> None:
    sp = glow_sprite(size)
    H, W = img.shape[:2]
    x0, y0 = int(round(cx - size / 2)), int(round(cy - size / 2))
    x1, y1 = x0 + size, y0 + size
    sx0, sy0 = max(0, -x0), max(0, -y0)
    sx1, sy1 = size - max(0, x1 - W), size - max(0, y1 - H)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    region = img[max(0, y0) : max(0, y0) + (sy1 - sy0), max(0, x0) : max(0, x0) + (sx1 - sx0)]
    region += sp[sy0:sy1, sx0:sx1, None] * (np.array(color, np.float32) * strength)


_LOGOS: dict = {}


def load_logo(name: str, box: int) -> Image.Image:
    """Load a logo PNG and knock out any white / checkerboard background that
    touches the image border (keeps white *inside* the mark)."""
    key = (name, box)
    if key in _LOGOS:
        return _LOGOS[key]
    im = Image.open(os.path.join(LOGO_DIR, f"{name}.png")).convert("RGBA")
    im.thumbnail((360, 360), Image.LANCZOS)
    a = np.array(im).astype(np.int16)
    rgb = a[..., :3]
    lo, hi = rgb.min(axis=2), rgb.max(axis=2)
    bg_like = (lo > 170) & ((hi - lo) < 28) & (a[..., 3] > 0)
    # flood from the border through bg-like pixels
    reach = np.zeros_like(bg_like)
    reach[0, :] = bg_like[0, :]
    reach[-1, :] = bg_like[-1, :]
    reach[:, 0] = bg_like[:, 0]
    reach[:, -1] = bg_like[:, -1]
    while True:
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        grown &= bg_like
        if np.array_equal(grown, reach):
            break
        reach = grown
    alpha = a[..., 3].copy()
    alpha[reach] = 0
    out = np.concatenate([rgb.clip(0, 255), alpha[..., None]], axis=2).astype(np.uint8)
    im = Image.fromarray(out)
    im = im.crop(im.getbbox() or (0, 0, 1, 1))
    im.thumbnail((box, box), Image.LANCZOS)
    _LOGOS[key] = im
    return im


# ----------------------------------------------------------------------------- background
class Background:
    def __init__(self, W: int, H: int, T: float, u: float, seed: int = 11):
        self.W, self.H, self.T, self.u = W, H, T, u
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        px, py = xx / W, yy / H
        c_mid = np.array([9, 9, 12], np.float32)
        c_top = np.array([15, 12, 14], np.float32)
        c_warm = np.array([22, 13, 9], np.float32)
        base = c_mid + (c_top - c_mid) * (1 - py)[..., None] + (c_warm - c_mid) * ((1 - px) * (1 - py))[..., None] * 0.9
        r = np.sqrt(((px - 0.5) * 1.1) ** 2 + ((py - 0.5) * 1.0) ** 2)
        self.vig = np.clip(1.22 - r * 1.05, 0.5, 1.0)[..., None].astype(np.float32)
        self.base = base.astype(np.float32)

        rng = random.Random(seed)
        n = int(44 * (W * H) / (1920 * 1080) + 14)
        self.nodes = []
        for _ in range(n):
            self.nodes.append(
                dict(
                    bx=rng.uniform(0.02, 0.98) * W,
                    by=rng.uniform(0.02, 0.98) * H,
                    ax=rng.uniform(26, 70) * u,
                    ay=rng.uniform(26, 70) * u,
                    k1=rng.choice([1, 1, 2]),
                    k2=rng.choice([1, 2, 2]),
                    p1=rng.uniform(0, math.tau),
                    p2=rng.uniform(0, math.tau),
                    r=rng.uniform(1.6, 3.4) * u,
                )
            )
        self.link_d = 300 * u
        # pulses travel along pairs that stay reasonably close
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.nodes[i], self.nodes[j]
                if math.hypot(a["bx"] - b["bx"], a["by"] - b["by"]) < self.link_d * 0.75:
                    pairs.append((i, j))
        rng.shuffle(pairs)
        self.pulses = [(i, j, rng.choice([2, 3, 4]), rng.random()) for i, j in pairs[:14]]
        self.dust = [
            (rng.random() * W, rng.random() * H, rng.uniform(0.8, 1.9) * u, rng.uniform(0.25, 0.9), rng.choice([1, 2, 3]), rng.uniform(0, math.tau))
            for _ in range(int(150 * (W * H) / (1920 * 1080) + 40))
        ]

    def node_pos(self, nd, t):
        w = math.tau * t / self.T
        return (nd["bx"] + nd["ax"] * math.sin(w * nd["k1"] + nd["p1"]), nd["by"] + nd["ay"] * math.sin(w * nd["k2"] + nd["p2"]))

    def render(self, t: float) -> Image.Image:
        W, H, T, u = self.W, self.H, self.T, self.u
        img = self.base.copy()
        w = math.tau * t / T
        # drifting orange glow (upper-left) and faint warm glow (lower-right)
        add_glow(img, W * (0.30 + 0.05 * math.sin(w)), H * (0.32 + 0.06 * math.sin(w * 2 + 1.3)), int(min(W, H) * 1.55), ORANGE, 0.17 + 0.02 * math.sin(w * 3))
        add_glow(img, W * (0.78 + 0.04 * math.cos(w)), H * (0.80 + 0.05 * math.sin(w + 2.0)), int(min(W, H) * 1.2), (120, 70, 50), 0.14)
        img *= self.vig
        frame = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")

        # --- network layer (warm white) and pulses (orange)
        mask = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(mask)
        pts = [self.node_pos(nd, t) for nd in self.nodes]
        P = np.array(pts, np.float32)
        D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
        ii, jj = np.where(np.triu(D < self.link_d, 1))
        for i, j in zip(ii, jj):
            a = (1 - D[i, j] / self.link_d) ** 1.6
            d.line([pts[i], pts[j]], fill=int(95 * a), width=max(1, int(round(1.4 * u))))
        for (x, y), nd in zip(pts, self.nodes):
            r = nd["r"]
            d.ellipse((x - r, y - r, x + r, y + r), fill=150)
        for x0, y0, r, a, k, ph in self.dust:
            y = (y0 - (t / T) * H * k * 0.35) % H
            x = (x0 + 18 * u * math.sin(w * 2 + ph)) % W
            tw = 0.55 + 0.45 * math.sin(w * k + ph)
            d.ellipse((x - r, y - r, x + r, y + r), fill=int(120 * a * tw))
        mask = mask.filter(ImageFilter.GaussianBlur(0.8 * u))
        net = Image.new("RGBA", (W, H), (255, 205, 180, 0))
        net.putalpha(mask)
        frame.alpha_composite(net)

        pm = Image.new("L", (W, H), 0)
        pd = ImageDraw.Draw(pm)
        for i, j, k, ph in self.pulses:
            s = ((t / T) * k + ph) % 1.0
            x = pts[i][0] + (pts[j][0] - pts[i][0]) * s
            y = pts[i][1] + (pts[j][1] - pts[i][1]) * s
            r = 4.2 * u
            pd.ellipse((x - r, y - r, x + r, y + r), fill=255)
        glow = pm.filter(ImageFilter.GaussianBlur(7 * u))
        g = Image.new("RGBA", (W, H), ORANGE + (0,))
        g.putalpha(glow.point(lambda v: min(255, int(v * 1.8))))
        frame.alpha_composite(g)
        core = Image.new("RGBA", (W, H), LIGHT_ORANGE + (0,))
        core.putalpha(pm.filter(ImageFilter.GaussianBlur(1.2 * u)))
        frame.alpha_composite(core)
        return frame


# ----------------------------------------------------------------------------- scenes
class Trailer:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.V = H > W
        self.u = min(W, H) / 1080.0
        self.bg = Background(W, H, DURATION, self.u)
        p = PROFILE["profile"]
        self.name = p["name"]
        self.title = p["title"]
        self.scenes = [
            # (start, end, fade_in, fade_out, fn)
            (0.0, 3.6, 0.0, 0.55, self.scene_title),
            (3.3, 7.1, 0.5, 0.55, self.scene_impact),
            (6.8, 10.6, 0.5, 0.55, self.scene_stack),
            (10.3, 13.4, 0.5, 0.55, self.scene_experience),
            (13.1, DURATION, 0.5, 0.6, self.scene_outro),
        ]
        self._edge_mask = None

    def px(self, v: float) -> float:
        return v * self.u

    # ---- shared bits
    def headline(self, layer, lines, size, y_center, p, weight="Bold", color=WHITE, glow=True, line_gap=1.06):
        """Fade/rise-in headline centered horizontally, centered vertically on y_center."""
        if p <= 0:
            return
        fnt = F(self.px(size), weight)
        lh = self.px(size) * line_gap
        total = lh * len(lines)
        e = ease_out_cubic(p)
        for i, line in enumerate(lines):
            tl, ox, oy = text_layer(line, fnt, color, alpha=e, blur=(1 - e) * 10, glow=ORANGE if glow else None, glow_r=int(self.px(22)), glow_a=0.22)
            x = (self.W - fnt.getlength(line)) / 2
            y = y_center - total / 2 + i * lh + (1 - e) * self.px(36)
            blit(layer, tl, x + ox, y + oy)

    def label(self, layer, txt, size, y, p, color=ORANGE, alpha=1.0, tracking=None):
        if p <= 0:
            return
        fnt = F(self.px(size), "SemiBold")
        tr = self.px(6) if tracking is None else tracking
        e = ease_out_cubic(p)
        tl, ox, oy = text_layer(txt, fnt, color, alpha=e * alpha, tracking=tr)
        x = (self.W - tracked_width(txt, fnt, tr)) / 2
        blit(layer, tl, x + ox, y + (1 - e) * self.px(16) + oy)

    # ---- scene 1: name reveal
    def scene_title(self, layer, lt, t):
        W, H, V, px = self.W, self.H, self.V, self.px
        size = px(118) if V else px(150)
        fnt = F(size, "Bold")
        lines = self.name.split(" ") if V else [self.name]
        lh = size * 1.02
        total = lh * len(lines)
        cy = H * (0.42 if V else 0.45)
        idx = 0
        for li, line in enumerate(lines):
            x0 = (W - fnt.getlength(line)) / 2
            y = cy - total / 2 + li * lh
            for i, ch in enumerate(line):
                st = 0.12 + idx * 0.055
                idx += 1
                if ch == " ":
                    continue
                p = ease_out_cubic(fit(lt, st, st + 0.75))
                if p <= 0:
                    continue
                cx = x0 + fnt.getlength(line[:i])
                gl, ox, oy = text_layer(ch, fnt, WHITE, alpha=p, blur=(1 - p) * 7, glow=ORANGE, glow_r=int(px(26)), glow_a=0.28 * p)
                blit(layer, gl, cx + ox, y + (1 - p) * size * 0.32 + oy)
        # orange rule
        p = ease_out_cubic(fit(lt, 0.95, 1.75))
        if p > 0:
            d = ImageDraw.Draw(layer)
            hw = px(90) * p
            y = cy + total / 2 + px(34)
            d.rounded_rectangle((W / 2 - hw, y - px(1.5), W / 2 + hw, y + px(1.5)), radius=px(2), fill=ORANGE + (int(255 * p),))
        # subtitle
        self.label(layer, self.title.upper(), 26 if not V else 24, cy + total / 2 + px(64), fit(lt, 1.25, 2.05))
        # meta line
        meta = "LLMs  ·  RAG  ·  Agent Workflows  ·  Model Serving  ·  MLOps"
        if V:
            meta = "LLMs · RAG · Agents · MLOps"
        p = fit(lt, 1.65, 2.45)
        if p > 0:
            fnt2 = F(px(24), "Regular")
            e = ease_out_cubic(p)
            tl, ox, oy = text_layer(meta, fnt2, WHITE, alpha=0.6 * e)
            blit(layer, tl, (W - fnt2.getlength(meta)) / 2 + ox, cy + total / 2 + px(118) + (1 - e) * px(14) + oy)

    # ---- scene 2: impact stats
    def scene_impact(self, layer, lt, t):
        W, H, V, px = self.W, self.H, self.V, self.px
        lines = ["Production AI,", "end to end."] if V else ["Production AI, end to end."]
        self.headline(layer, lines, 84 if not V else 86, H * (0.30 if V else 0.30), fit(lt, 0.0, 0.8))
        sub = "From retrieval and inference to Kubernetes and on-call."
        if V:
            sub = "Retrieval, inference, serving, on-call."
        p = fit(lt, 0.25, 1.0)
        if p > 0:
            fnt = F(px(28), "Regular")
            e = ease_out_cubic(p)
            tl, ox, oy = text_layer(sub, fnt, WHITE, alpha=0.62 * e)
            blit(layer, tl, (W - fnt.getlength(sub)) / 2 + ox, H * (0.30 if V else 0.30) + px(74 if not V else 120) + (1 - e) * px(14) + oy)

        chips = [
            ("", "15", "+", "years in software engineering"),
            ("", "6", "+", "years shipping production ML"),
            ("~", "35", "%", "better GPU utilization"),
            ("", "15", "%", "lower retrieval latency"),
        ]
        if V:
            cw, ch, gap = px(470), px(176), px(26)
            cols = 2
        else:
            cw, ch, gap = px(396), px(156), px(26)
            cols = 4
        rows = math.ceil(len(chips) / cols)
        grid_w = cols * cw + (cols - 1) * gap
        grid_h = rows * ch + (rows - 1) * gap
        gx = (W - grid_w) / 2
        gy = H * (0.60 if V else 0.62) - grid_h / 2
        for i, (pre, num, suf, lab) in enumerate(chips):
            st = 0.45 + i * 0.14
            p = fit(lt, st, st + 0.7)
            if p <= 0:
                continue
            e = ease_out_cubic(p)
            cnt = ease_out_expo(fit(lt, st, st + 1.3))
            shown = int(round(int(num) * cnt))
            card = rounded_rect_layer(cw, ch, px(26), (255, 255, 255, 13), (255, 255, 255, 48), max(1, int(px(2))))
            d = ImageDraw.Draw(card)
            fn = F(px(58), "Bold")
            fs = F(px(32), "SemiBold")
            fl = F(px(22), "Regular")
            nx, ny = px(34), px(22)
            x = nx
            if pre:
                d.text((x, ny + px(14)), pre, font=fs, fill=LIGHT_ORANGE + (255,))
                x += fs.getlength(pre) + px(2)
            d.text((x, ny), str(shown), font=fn, fill=ORANGE + (255,))
            x += fn.getlength(str(shown)) + px(4)
            d.text((x, ny + px(22)), suf, font=fs, fill=LIGHT_ORANGE + (255,))
            # accent tick between number and label
            ty = ny + px(72)
            d.rounded_rectangle((nx, ty, nx + px(28), ty + px(3)), radius=px(2), fill=ORANGE + (200,))
            # label (wrap if needed), anchored to the card bottom
            words, line = lab.split(), ""
            maxw = cw - 2 * nx
            out_lines = []
            for wd in words:
                cand = (line + " " + wd).strip()
                if fl.getlength(cand) > maxw and line:
                    out_lines.append(line)
                    line = wd
                else:
                    line = cand
            out_lines.append(line)
            ly = ch - px(24) - fl.getmetrics()[0] - fl.getmetrics()[1]
            for k, ln in enumerate(reversed(out_lines)):
                d.text((nx, ly - k * px(26)), ln, font=fl, fill=WHITE + (190,))
            card = with_alpha(scale_about_center(card, 0.92 + 0.08 * e), e)
            col, row = i % cols, i // cols
            x = gx + col * (cw + gap)
            y = gy + row * (ch + gap) + (1 - e) * px(40)
            blit(layer, card, x, y)

    # ---- scene 3: stack tiles
    def scene_stack(self, layer, lt, t):
        W, H, V, px = self.W, self.H, self.V, self.px
        lines = ["Shipped with a", "modern AI stack."] if V else ["Shipped with a modern AI stack."]
        self.headline(layer, lines, 72 if not V else 80, H * (0.27 if V else 0.28), fit(lt, 0.0, 0.8))
        self.label(layer, "PYTHON  ·  LLMS & RAG  ·  FASTAPI  ·  PYTORCH  ·  KUBERNETES" if not V else "CORE STACK", 20, H * (0.27 if V else 0.28) + px(66 if not V else 116), fit(lt, 0.2, 0.9), alpha=0.9)
        tiles = [
            ("python", "Python"),
            ("pytorch", "PyTorch"),
            ("fastapi", "FastAPI"),
            ("langchain", "LangChain"),
            ("kubernetes", "Kubernetes"),
            ("react", "React"),
        ]
        if V:
            tile, gap, cols = px(262), px(44), 3
        else:
            tile, gap, cols = px(204), px(44), 6
        rows = math.ceil(len(tiles) / cols)
        grid_w = cols * tile + (cols - 1) * gap
        grid_h = rows * (tile + px(56)) + (rows - 1) * gap
        gx = (W - grid_w) / 2
        gy = H * (0.60 if V else 0.62) - grid_h / 2
        fl = F(px(22), "Medium")
        for i, (nm, lab) in enumerate(tiles):
            st = 0.4 + i * 0.1
            p = fit(lt, st, st + 0.75)
            if p <= 0:
                continue
            e = ease_out_cubic(p)
            s = 0.6 + 0.4 * ease_out_back(p)
            card = rounded_rect_layer(tile, tile, px(34), (255, 255, 255, 12), (255, 255, 255, 46), max(1, int(px(2))))
            logo = load_logo(nm, int(tile * 0.52))
            if nm == "fastapi":
                logo = load_logo(nm, int(tile * 0.74))
            blit(card, logo, (card.size[0] - logo.size[0]) / 2, (card.size[1] - logo.size[1]) / 2)
            card = with_alpha(scale_about_center(card, s), e)
            col, row = i % cols, i // cols
            bob = math.sin(t * 2.1 + i * 0.9) * px(2.5)
            x = gx + col * (tile + gap)
            y = gy + row * (tile + px(56) + gap) + bob
            blit(layer, card, x, y)
            tl, ox, oy = text_layer(lab, fl, WHITE, alpha=0.8 * e)
            blit(layer, tl, x + (tile - fl.getlength(lab)) / 2 + ox, y + tile + px(18) + oy)

    def edge_mask(self) -> Image.Image:
        if self._edge_mask is None:
            W = self.W
            fade = int(W * 0.14)
            arr = np.ones(W, np.float32)
            ramp = np.linspace(0, 1, fade, dtype=np.float32)
            arr[:fade] = ramp
            arr[-fade:] = ramp[::-1]
            self._edge_mask = (arr * 255).astype(np.uint8)
        return self._edge_mask

    def ticker(self, layer, items, y, speed, lt, size, alpha, direction=1):
        W, px = self.W, self.px
        fnt = F(px(size), "SemiBold")
        dot_r, pad = px(6), px(44)
        widths = [fnt.getlength(s) for s in items]
        seq_w = sum(widths) + len(items) * (2 * pad + 2 * dot_r)
        asc, desc = fnt.getmetrics()
        h = asc + desc + int(px(20))
        strip = Image.new("RGBA", (W, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(strip)
        off = (lt * speed) % seq_w
        x = -off if direction > 0 else off - seq_w
        # draw enough copies to cover the strip
        while x < W:
            cx = x
            for s, w in zip(items, widths):
                d.text((cx, px(10)), s, font=fnt, fill=WHITE + (int(255 * 0.86),))
                cx += w + pad
                d.ellipse((cx - dot_r, h / 2 - dot_r, cx + dot_r, h / 2 + dot_r), fill=ORANGE + (255,))
                cx += 2 * dot_r + pad
            x += seq_w
        a = np.array(strip.getchannel("A"), np.float32) * (self.edge_mask()[None, :] / 255.0) * alpha
        strip.putalpha(Image.fromarray(a.astype(np.uint8)))
        blit(layer, strip, 0, y - h / 2)

    # ---- scene 4: experience ticker
    def scene_experience(self, layer, lt, t):
        W, H, V, px = self.W, self.H, self.V, self.px
        self.label(layer, "EXPERIENCE", 22, H * (0.30 if V else 0.30), fit(lt, 0.0, 0.7))
        lines = ["Trusted on teams at"] if not V else ["Trusted on", "teams at"]
        self.headline(layer, lines, 66 if not V else 78, H * (0.30 if V else 0.30) + px(84 if not V else 130), fit(lt, 0.1, 0.9))
        employers = ["Novawave", "Larynx", "NextEra Energy", "Datex", "FIS", "Microsoft", "Google"]
        e = ease_out_cubic(fit(lt, 0.35, 1.1))
        if e > 0:
            if V:
                self.ticker(layer, employers, H * 0.56, px(150), lt, 70, e, 1)
                self.ticker(layer, ["Healthcare AI", "Enterprise LLM Apps", "Energy ML", "Logistics", "Fintech", "Cloud Platforms"], H * 0.64, px(120), lt, 44, e * 0.75, -1)
            else:
                self.ticker(layer, employers, H * 0.585, px(170), lt, 64, e, 1)
                self.ticker(layer, ["Healthcare AI", "Enterprise LLM Applications", "Energy ML Platforms", "Logistics", "Fintech", "Cloud Platforms"], H * 0.69, px(130), lt, 34, e * 0.7, -1)

    # ---- scene 5: outro
    def scene_outro(self, layer, lt, t):
        W, H, V, px = self.W, self.H, self.V, self.px
        lines = ["Let's build", "something", "intelligent."] if V else ["Let's build something intelligent."]
        self.headline(layer, lines, 80 if not V else 92, H * (0.42 if V else 0.44), fit(lt, 0.0, 0.85))
        p = fit(lt, 0.45, 1.1)
        if p > 0:
            e = ease_out_cubic(p)
            self.label(layer, "SCROLL TO EXPLORE", 20, H * (0.44 if not V else 0.42) + px(96 if not V else 190), p, color=WHITE, alpha=0.55)
            d = ImageDraw.Draw(layer)
            bob = (math.sin(lt * 4.2) * 0.5 + 0.5) * px(10)
            cx, cy = W / 2, H * (0.44 if not V else 0.42) + px(150 if not V else 246) + bob
            s = px(11)
            d.line([(cx - s, cy - s / 2), (cx, cy + s / 2), (cx + s, cy - s / 2)], fill=ORANGE + (int(255 * e),), width=max(2, int(px(3))), joint="curve")

    # ---- HUD (static => loop safe)
    def hud(self, canvas):
        W, H, V, px = self.W, self.H, self.V, self.px
        fnt = F(px(17), "SemiBold")
        tr = px(4)
        m = px(60 if not V else 50)
        tl, ox, oy = text_layer(self.name.upper(), fnt, WHITE, alpha=0.5, tracking=tr)
        blit(canvas, tl, m + ox, m + oy)
        right = "APPLIED AI / ML ENGINEERING"
        tl, ox, oy = text_layer(right, fnt, WHITE, alpha=0.5, tracking=tr)
        blit(canvas, tl, W - m - tracked_width(right, fnt, tr) + ox, m + oy)
        d = ImageDraw.Draw(canvas)
        d.line([(m, m + px(34)), (m + px(44), m + px(34))], fill=ORANGE + (220,), width=max(1, int(px(2))))

    def dots(self, canvas, t):
        W, H, px = self.W, self.H, self.px
        d = ImageDraw.Draw(canvas)
        n = len(self.scenes)
        active = 0
        for i, (t0, t1, *_rest) in enumerate(self.scenes):
            if t >= t0 + 0.25:
                active = i
        r, gap = px(4), px(20)
        total = n * 2 * r + (n - 1) * gap
        x = (W - total) / 2 + r
        y = H - px(58)
        for i in range(n):
            if i == active:
                d.rounded_rectangle((x - r - px(8), y - r, x + r + px(8), y + r), radius=r, fill=ORANGE + (255,))
                x += px(16)
            else:
                d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE + (80,))
            x += 2 * r + gap

    # ---- frame
    def frame(self, t: float) -> Image.Image:
        W, H = self.W, self.H
        canvas = self.bg.render(t)
        for t0, t1, din, dout, fn in self.scenes:
            if t < t0 or t >= t1:
                continue
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fn(layer, t - t0, t)
            xp = fit(t, t1 - dout, t1)
            if xp > 0:
                e = ease_in_out(xp)
                layer = scale_about_center(layer, 1 + 0.05 * e)
                if e > 0.05:
                    layer = layer.filter(ImageFilter.GaussianBlur(e * self.px(9)))
                layer = with_alpha(layer, 1 - e)
            canvas.alpha_composite(layer)
        self.hud(canvas)
        self.dots(canvas, t)
        return canvas


# ----------------------------------------------------------------------------- main
def render(variant: str, out_path: str, preview_dir: str | None = None) -> None:
    W, H = (1080, 1920) if variant == "portrait" else (1920, 1080)
    tr = Trailer(W, H)
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        for tt in PREVIEW_TIMES:
            tr.frame(tt).convert("RGB").save(os.path.join(preview_dir, f"{variant}_{tt:05.2f}.png"))
        print(f"previews written to {preview_dir}")
        return

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    n = int(round(DURATION * FPS))
    cmd = [
        ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_start = time.time()
    for i in range(n):
        fr = tr.frame(i / FPS).convert("RGB")
        proc.stdin.write(fr.tobytes())
        if i % 60 == 0:
            el = time.time() - t_start
            print(f"  {variant}: frame {i}/{n}  ({el:.0f}s elapsed)", flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg failed with code {proc.returncode}")
    print(f"wrote {out_path} ({os.path.getsize(out_path) / 1e6:.1f} MB) in {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    preview = None
    if "--preview" in args:
        k = args.index("--preview")
        preview = args[k + 1]
        del args[k : k + 2]
    variants = args or ["landscape", "portrait"]
    outs = {"landscape": os.path.join(VIDEO_DIR, "test_trailer.mp4"), "portrait": os.path.join(VIDEO_DIR, "test_trailer_vertical.mp4")}
    for v in variants:
        if v not in outs:
            raise SystemExit(f"unknown variant {v!r}; use landscape or portrait")
        render(v, outs[v], preview)
