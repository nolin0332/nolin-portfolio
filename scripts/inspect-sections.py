#!/usr/bin/env python3
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
h = (Path(__file__).resolve().parents[1] / "public" / "index.html").read_text(encoding="utf-8")

def chunk(sid):
    start = h.find(f'id="{sid}"')
    nxt = h.find('id="story-', start + 10)
    return h[start : nxt if nxt > start else start + 4000]

for sid in [
    "story-gamification-leaderboard-ladder",
    "story-gamification-xp",
    "story-airdrops-post-seasons",
    "story-airdrops-pre-hero",
    "story-airdrops-pre-end",
    "story-rewards-hero",
]:
    c = chunk(sid)
    print("===", sid, "===")
    for pat, label in [
        (r'<h[12][^>]*class="story-feature-title"[^>]*>(.*?)</h[12]>', "title"),
        (r'<h4[^>]*class="story-feature-desc"[^>]*>(.*?)</h4>', "desc"),
        (r'<li[^>]*>(.*?)</li>', "li"),
        (r'id="story-airdrops-pre-end-card-\d-title"[^>]*>([^<]+)', "cardtitle"),
    ]:
        for i, m in enumerate(re.finditer(pat, c, re.DOTALL)):
            t = re.sub(r"\s+", " ", m.group(1).strip())[:180]
            print(f"  {label}{i}: {t}")
    print()
