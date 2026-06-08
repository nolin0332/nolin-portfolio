from pathlib import Path

js = Path("public/_astro/hoisted.jm-mpcuc8bi.js").read_text(encoding="utf-8")
start = js.find("class ScrollManager extends")
end = js.find("class DeckOverlayScrollManager", start)
print(js[start:end][:3500])
print("\n---PRELOADER---\n")
start2 = js.find("class Preloader")
end2 = js.find("const preloader=new Preloader", start2)
print(js[start2:end2][:2500])
