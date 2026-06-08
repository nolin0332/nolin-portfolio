import re
from pathlib import Path

h = Path("public/index.html").read_text(encoding="utf-8")
for sid in ["story-rewards-hero", "story-rewards-referral"]:
    start = h.find(f'id="{sid}"')
    end = h.find('id="story-', start + 10)
    chunk = h[start:end]
    print(sid, "exp-achievement:", "exp-achievement" in chunk)
    for m in re.finditer(r"<p class=\"exp-achievement\".*?</p>", chunk, re.DOTALL):
        print(" ", m.group(0)[:180])
