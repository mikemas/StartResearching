// Refreshes content-inventory.txt from the live Squarespace sitemap,
// and tries Squarespace blog RSS/JSON endpoints for import staging.
// Usage: npm run import:squarespace
import { writeFile, mkdir } from 'node:fs/promises';

const SITE = 'https://www.startresearching.com';
const OUT_INVENTORY = new URL('../content-inventory.txt', import.meta.url);
const OUT_DIR = new URL('../src/content/blog/', import.meta.url);

async function getText(url) {
  const res = await fetch(url, { headers: { 'User-Agent': 'StartResearching-migration/1.0' } });
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return await res.text();
}

const sitemap = await getText(`${SITE}/sitemap.xml`);
const locs = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map((m) => m[1]);
await writeFile(OUT_INVENTORY, locs.join('\n'));
console.log(`inventory: ${locs.length} urls -> content-inventory.txt`);

// Squarespace commonly exposes RSS at /blog?format=rss and JSON at ?format=json
for (const feed of [`${SITE}/blog?format=rss`, `${SITE}/?format=rss`]) {
  try {
    const xml = await getText(feed);
    await mkdir(new URL('../tmp/', import.meta.url), { recursive: true });
    const safe = feed.replace(/[^a-z0-9]+/gi, '_');
    await writeFile(new URL(`../tmp/${safe}.xml`, import.meta.url), xml);
    console.log(`saved feed: ${feed} (${xml.length} bytes)`);
  } catch (e) {
    console.log(`feed miss: ${feed} (${e.message})`);
  }
}
console.log(`blog dir ready: ${OUT_DIR.pathname}`);
console.log('Next: parse tmp/*.xml into src/content/blog/*.md');
