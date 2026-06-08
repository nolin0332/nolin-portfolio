import re
h = open("public/index.html", encoding="utf-8").read()
m = re.search(r'id="story-airdrops-post-seasons-title"[^>]*>([^<]+)', h)
print("seasons title:", m.group(1) if m else "N/A")
m2 = re.search(
    r'id="story-airdrops-post-seasons".*?story-feature-desc">([^<]{0,160})',
    h,
    re.DOTALL,
)
print("seasons desc:", m2.group(1)[:120] if m2 else "N/A")
print("J+ years:", "J+ years" in h)
print("tagline in meta:", "RAG-based LLM" in h[:4000])
m = re.search(r'id="story-gamification-hero".*?story-feature-desc">(.{0,140})', h, re.DOTALL)
print("hero desc:", m.group(1) if m else "missing")
m2 = re.search(r'class="skills-cats">(.{0,700})', h, re.DOTALL)
body = m2.group(1) if m2 else ""
print("skill-cat count:", body.count("skill-cat"))
print("duplicate Languages:", body.count("Languages"))
print("email:", "michael.trent039@gmail.com" in h)
print("hotmail:", "hotmail.com" in h)
