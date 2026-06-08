from pathlib import Path

js = Path("public/_astro/hoisted.jm-mpcuc8bi.js").read_text(encoding="utf-8")
start = js.find("class StoryAirdropsPostSeasonsSlide")
end = js.find("const storyAirdropsPostSeasonsSlide", start)
print(js[start:end][:4000])
