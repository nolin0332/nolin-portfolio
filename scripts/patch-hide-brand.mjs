import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const hoisted = path.join(root, "public/_astro/hoisted.jm-mpcuc8bi.js");

let t = fs.readFileSync(hoisted, "utf8");

const repls = [
  [
    'update(o){let a=math.fit(properties.startTimeAfterStartButtonClick,1,2,-100,0,ease.cubicOut);this.domContainer.style.transform=`translateY(${a}px)`}',
    'update(o){this.domContainer&&(this.domContainer.style.display="none",this.domContainer.style.transform=`translateY(${math.fit(properties.startTimeAfterStartButtonClick,1,2,-100,0,ease.cubicOut)}px)`)',
  ],
  [
    "this.ufxMesh.renderOrder=10,preUfx.scene.add(this.ufxMesh)",
    "this.ufxMesh.renderOrder=10",
  ],
  ["this.ufxMesh.visible=v>0", "this.ufxMesh.visible=!1"],
  [
    'this.domVideoPlayButton.addEventListener("click",()=>{this.isVideoActive=!0,videoOverlay.initAndPlayVideo()})',
    'this.domVideoPlayButton.addEventListener("click",()=>{})',
  ],
  [
    "this.isVideoPlaying=u>.12&&this.domRange.hideScreenOffset<0",
    "this.isVideoPlaying=!1",
  ],
];

for (const [old, neu] of repls) {
  if (!t.includes(old)) {
    console.error("Missing pattern:", old.slice(0, 70));
    process.exit(1);
  }
  t = t.replace(old, neu);
}

fs.writeFileSync(hoisted, t);
console.log("Patched hoisted.js — header, video, marketplace UI disabled");
