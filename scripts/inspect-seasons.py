#!/usr/bin/env python3
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
h = (Path(__file__).resolve().parents[1] / "public" / "index.html").read_text(encoding="utf-8")
start = h.find('id="story-airdrops-post-seasons"')
nxt = h.find('id="story-', start + 10)
print(h[start:nxt if nxt > start else start + 2500])
