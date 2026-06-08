import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');

/** Canonical paths only — correct prefix per asset type */
const paths = [
  // HTML/CSS/favicon
  '_astro/index.Ew-YyTBx.css',
  '_astro/hoisted.jm-mpcuc8bi.js',
  'favicon/apple-touch-icon.png',
  'favicon/favicon-16x16.png',
  'favicon/favicon-32x32.png',
  'favicon/favicon.ico',
  'favicon/safari-pinned-tab.svg',
  'favicon/site.webmanifest',
  'favicon/browserconfig.xml',
  'index.htm',
  'assets/meta/cover.png',
  // fonts
  ...['Regular', 'Medium', 'SemiBold', 'Bold'].flatMap((w) => [
    `assets/fonts/GolosText-${w}.woff2`,
    `assets/fonts/GolosText-${w}.woff`,
  ]),
  // svg/images from html
  'assets/images/shadow.png',
  'assets/svg/arrow-right.svg',
  'assets/svg/navigation/play.svg',
  'assets/svg/navigation/game.svg',
  'assets/svg/navigation/rewards.svg',
  'assets/svg/navigation/airdrops.svg',
  'assets/svg/navigation/join.svg',
  // deck
  'assets/images/deck/card-frame.svg',
  'assets/images/deck/card-empty.svg',
  ...[
    'complete-quests', 'earn-xp', 'progress-in-ranks', 'mystery-chests',
    'ascend-the-leaderboard', 'invite-to-earn', 'trade-to-earn', 'stake-to-earn',
    'future-gaming-hub', 'battle-pass-airdrops', 'spaace-arena', 'enter-the-arena',
  ].flatMap((n) => [
    `assets/images/deck/${n}.jpg`,
    `assets/images/deck/${n}.png`,
  ]),
  // css images
  'assets/images/xp_logo.png',
  'assets/images/quest-xp-icon-empty.png',
  'assets/images/quest-xp-icon-checked-base.png',
  'assets/images/quest-xp-icon-checked-tick.png',
  'assets/images/airdrops/rank.png',
  'assets/images/airdrops/rank-item01.png',
  'assets/images/airdrops/rank-item02.png',
  'assets/images/airdrops/xp.png',
  'assets/images/airdrops/xp-item01.png',
  'assets/images/airdrops/coin.png',
  'assets/images/airdrops/coin-item01.png',
  'assets/images/leaderboard/1.png',
  'assets/images/leaderboard/2.png',
  'assets/images/leaderboard/3.png',
  'assets/images/leaderboard/4.png',
  'assets/images/leaderboard/5.png',
  // videos
  'assets/videos/test_trailer.mp4',
  'assets/videos/test_trailer_vertical.mp4',
];

// models
const models = [
  'Hex_Ring.buf', 'Hex_Ring_New.buf',
  'coin/coin_md.buf',
  'logo/logo.buf', 'logo/logo_shell.buf',
  'end/astronaut.buf', 'end/astronaut_animation.buf', 'end/rock.buf',
  'staking_network/Network_point_ref.buf',
  'staking_network/Network_segment_ref.buf',
  'staking_network/Network_segments.buf',
  'staking_network/Staking_eth_tip_points.buf',
  'staking_network/Staking_trail.buf',
  'staking_network/Staking_eth_tip_inner.buf',
  'staking_network/Staking_eth_tip_outer.buf',
  'staking_network/Staking_eth_rest_inner.buf',
  'staking_network/Staking_eth_rest_outer.buf',
];
models.forEach((m) => paths.push(`assets/models/${m}`));
for (let i = 0; i < 4; i++) {
  paths.push(`assets/models/Terrain_main_${i}.buf`);
  paths.push(`assets/models/Terrain_sided_${i}.buf`);
}

// textures (canonical TEXTURE_PATH)
const textures = [
  'LDR_RGB1_0.png', 'bg.png', 'hex_icon.png', 'logo.png', 'logo_shade.png',
  'logo_transition.jpg', 'network_gradient.png', 'profiles.png', 'wrink_nor.png',
  'lens_dirt.jpg', 'coin_matcap.jpg', 'coin_shadow.png',
  'coin/coin_ao_id.png', 'coin/coin_md_nor.png',
  'end/BG.webp', 'end/astronaut.webp', 'end/astronaut_light.webp',
  'end/portal_nebula.webp', 'end/portal_nebula_blur.webp', 'end/portal_stars.webp', 'end/rock.png',
  'gamificationQuests/logo_mask.png', 'gamificationQuests/xp.png',
  'gamificationQuests/quest_1_card_1.png', 'gamificationQuests/quest_1_card_2.png',
  'gamificationQuests/quest_1_card_3.png', 'gamificationQuests/quest_2_card.png',
  'gamificationQuests/quest_3_card.png', 'gamificationQuests/stylish_mask.webp',
  'storyGamificationChests/box_close.webp', 'storyGamificationChests/box_close_alpha.webp',
  'storyGamificationChests/box_close_light.webp', 'storyGamificationChests/box_close_light_alpha.webp',
  'storyGamificationChests/box_open.webp', 'storyGamificationChests/box_open_alpha.webp',
  'storyGamificationChests/box_open_light.webp', 'storyGamificationChests/box_open_light_alpha.webp',
  'storyGamificationChests/chest_particle.png', 'storyGamificationChests/gems_alpha.png',
  'storyGamificationChests/gems_rgb.png', 'storyGamificationStaking/glass.png',
  'storyRewardsCashback/btn-buy.png', 'storyRewardsCashback/btn-sell.png',
  'storyRewardsCashback/card1.png', 'storyRewardsCashback/card2.png', 'storyRewardsCashback/card3.png',
  'storyAirdropPreEngagement/x-logo.png',
  'storyGamificationRanks/1-bronze.png', 'storyGamificationRanks/2-silver.png',
  'storyGamificationRanks/3-gold.png', 'storyGamificationRanks/4-platinum.png',
  'storyGamificationRanks/5-diamond.png',
];
textures.forEach((t) => paths.push(`assets/textures/${t}`));
for (let i = 1; i <= 5; i++) paths.push(`assets/textures/storyAirdropPostAvatars/${i}.png`);
for (const id of ['like', 'comment', 'repost', 'follow']) {
  paths.push(`assets/textures/storyAirdropPreEngagement/card-${id}.jpg`);
}

// audio - probe common spaace names
[
  'ambient.mp3', 'music.mp3', 'bgm.mp3', 'loop.mp3', 'soundtrack.mp3',
  'click.mp3', 'whoosh.mp3', 'intro.mp3', 'main.mp3', 'theme.mp3',
].forEach((a) => paths.push(`assets/audios/${a}`));

const bases = ['https://julio-modern.vercel.app', 'https://vision.spaace.io'];

async function download(rel) {
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 100) return { rel, status: 'skip' };
  for (const base of bases) {
    try {
      const res = await fetch(`${base}/${rel}`, { signal: AbortSignal.timeout(60000) });
      if (!res.ok) continue;
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length < 50) continue;
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, buf);
      return { rel, status: 'ok', size: buf.length, base };
    } catch {
      /* */
    }
  }
  return { rel, status: 'miss' };
}

const unique = [...new Set(paths)];
const results = [];
for (const rel of unique) {
  results.push(await download(rel));
}

const ok = results.filter((r) => r.status === 'ok');
const miss = results.filter((r) => r.status === 'miss');
const skip = results.filter((r) => r.status === 'skip');

console.log(`ok=${ok.length} skip=${skip.length} miss=${miss.length}`);
miss.forEach((r) => console.log('MISS', r.rel));
ok.filter((r) => r.size > 10000).forEach((r) => console.log('NEW', r.rel, r.size));

fs.writeFileSync(
  path.join(root, 'scripts/missed-assets.txt'),
  miss.map((r) => r.rel).join('\n'),
);
