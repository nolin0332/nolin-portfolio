#!/usr/bin/env python3
import re
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pp", ROOT / "scripts" / "personalize-portfolio.py")
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)

profile = pp.load_profile()
html = (ROOT / "public" / "index.html").read_text(encoding="utf-8")

def count(h):
    return len(re.findall(r"<div[\s>]", h)), h.count("</div>")

steps = []

def step(name, fn):
    global html
    html = fn(html)
    o, c = count(html)
    steps.append((name, o, c, o - c))

p = profile["profile"]
html = re.sub(r"<title>[^<]+</title>", f"<title>{p['name']} | {p['title']}</title>", html, count=1)

for section_id, content in profile["sections"].items():
    if section_id == "story-airdrops-post-seasons":
        if "titleHtml" in content:
            html = pp.set_element_text(html, "story-airdrops-post-seasons-title", content["titleHtml"])
        if "descHtml" in content:
            html = pp.set_desc(html, section_id, content["descHtml"])
        step(f"seasons {section_id}", lambda h: h)
        continue
    if "titleHtml" in content:
        html = pp.set_title(html, section_id, content["titleHtml"])
    if "descHtml" in content:
        html = pp.set_desc(html, section_id, content["descHtml"])
    if "bullets" in content:
        html = pp.set_bullet_list(html, section_id, content["bullets"])
    step(section_id, lambda h: h)

quests = profile["quests"]
html = pp.set_element_text(html, "story-gamification-quests-quest-number", quests["number"])
html = pp.set_element_text(html, "story-gamification-quests-quest-desc", quests["desc"])
html = pp.set_element_text(html, "story-gamification-quests-points", quests["points"])
step("quests overlay", lambda h: h)

xp = profile["xp"]
html = pp.set_title(html, "story-gamification-xp", xp["titleHtml"])
html = pp.set_xp_list(html, xp["items"])
step("xp", lambda h: h)

html = pp.set_skills_cats(html, profile["skills_cats"])
step("skills-cats", lambda h: h)

end = profile["end_hero"]
html = pp.set_title(html, "end-hero", end["titleHtml"])
html = pp.set_desc(html, "end-hero", end["descHtml"])
step("end-hero", lambda h: h)

print("start", count((ROOT / "public/index.html").read_text(encoding="utf-8")))
for s in steps:
    if s[1] != 230 or s[2] != 230:
        print("CHANGED", s)
