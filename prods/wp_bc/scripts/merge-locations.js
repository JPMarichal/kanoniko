const fs = require('fs');
const path = require('path');

const DATA_DIR = path.resolve(__dirname, '..', 'wp-content', 'plugins', 'bc-scripture-map', 'data');

// ── Helpers ──────────────────────────────────────────────
function roundCoord(v, decimals = 4) {
  return Math.round(v * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

function coordKey(lat, lng, precision = 2) {
  return `${roundCoord(lat, precision)},${roundCoord(lng, precision)}`;
}

function mapGnosisType(featureType, subType) {
  const t = (featureType || '').toLowerCase();
  const s = (subType || '').toLowerCase();

  if (t === 'water' && (s === 'river' || s === 'brook' || s === 'stream' || s === 'wadi')) return 'river';
  if (t === 'water') return 'sea';
  if (t === 'mountain') return 'mountain';
  if (t === 'valley') return 'region';
  if (t === 'region') return 'region';
  if (t === 'island') return 'region';
  if (t === 'landmark') return 'landmark';
  if (t === 'path') return 'region';
  if (t === 'city') return 'city';
  return 'city';
}

function confidenceFromSource(source) {
  if (source === 'openbible') return 'medium';
  if (source === 'theographic') return 'medium';
  return 'low';
}

// ── 1. Load Gnosis ───────────────────────────────────────
console.log('Loading Gnosis places.json...');
const gnosisRaw = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'gnosis-places.json'), 'utf8'));
const gnosisEntries = {};
Object.keys(gnosisRaw).forEach(k => {
  const p = gnosisRaw[k];
  if (!p.latitude || !p.longitude) return;
  gnosisEntries[p.id || k] = {
    id: p.id,
    name: p.name || p.esv_name || p.kjv_name,
    esvName: p.esv_name || p.name,
    lat: p.latitude,
    lng: p.longitude,
    type: mapGnosisType(p.feature_type, p.feature_sub_type),
    verses: p.verses || [],
    aliases: p.aliases || [],
    source: p.coordinate_source || 'openbible',
    confidence: confidenceFromSource(p.coordinate_source),
    openbibleId: p.openbible_id || null,
    theographicId: p.theographic_id || null,
    featureType: p.feature_type,
    featureSubType: p.feature_sub_type,
  };
});
console.log(`  → ${Object.keys(gnosisEntries).length} entries with coordinates`);

// ── 2. Load existing TSV ─────────────────────────────────
console.log('Loading existing TSV...');
const tsvLines = fs.readFileSync(path.join(DATA_DIR, 'openbible-places.tsv'), 'utf8').split('\n').filter(l => l.trim());
tsvLines.shift(); // header
const tsvEntries = [];
tsvLines.forEach(l => {
  const parts = l.split('\t');
  if (parts.length < 4) return;
  const esvName = parts[0].trim();
  const kmzName = (parts[1] || '').trim();
  tsvEntries.push({
    esvName,
    kmzName: kmzName || esvName,
    lat: parseFloat(parts[2]),
    lng: parseFloat(parts[3]),
    passages: (parts[4] || '').trim(),
    comment: (parts[5] || '').trim(),
  });
});
console.log(`  → ${tsvEntries.length} entries`);

// ── 3. Load CH ───────────────────────────────────────────
console.log('Loading Church History...');
const chEntries = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'church-history.json'), 'utf8'));
console.log(`  → ${chEntries.length} entries`);

// ── 4. Build TSV lookup by coord + name ──────────────────
const tsvByCoord = new Map();
tsvEntries.forEach(e => {
  const key = coordKey(e.lat, e.lng, 2);
  if (!tsvByCoord.has(key)) tsvByCoord.set(key, []);
  tsvByCoord.get(key).push(e);
});

// Also build lookup by English ESV name
const tsvByEsvName = new Map();
tsvEntries.forEach(e => {
  const name = e.esvName.toLowerCase().replace(/\s*\(\d+\)\s*$/, '').trim();
  tsvByEsvName.set(name, e);
});

// ── 5. Match Gnosis to existing TSV ──────────────────────
// For each Gnosis entry, check if it matches an existing TSV entry
// Priority: openbible_id > ESV name > aliases > coordinates (precise)
const matchedGnosisIds = new Set();
const nameOverride = new Map(); // gnosisId → spanishName

Object.keys(gnosisEntries).forEach(gId => {
  const g = gnosisEntries[gId];
  const esvLower = (g.esvName || '').toLowerCase().trim();
  const nameLower = (g.name || '').toLowerCase().trim();

  function tryMatchByName(searchName) {
    const clean = searchName.replace(/\s*\(\d+\)\s*$/, '').trim();
    if (tsvByEsvName.has(clean)) {
      matchedGnosisIds.add(gId);
      nameOverride.set(gId, tsvByEsvName.get(clean).kmzName);
      return true;
    }
    return false;
  }

  // 1. Try match by openbible_id
  if (g.openbibleId && tryMatchByName(g.openbibleId.toLowerCase())) return;

  // 2. Try match by ESV name
  if (esvLower && tryMatchByName(esvLower)) return;

  // 3. Try match by name
  if (nameLower && nameLower !== esvLower && tryMatchByName(nameLower)) return;

  // 4. Try alias matching
  for (const alias of g.aliases) {
    if (tryMatchByName(alias.toLowerCase().trim())) return;
  }

  // 5. Try match by coordinate (HIGH precision: 4 decimals ≈ 10m)
  const coordKey4 = coordKey(g.lat, g.lng, 4);
  if (tsvByCoord.has(coordKey4)) {
    const matches = tsvByCoord.get(coordKey4);
    matchedGnosisIds.add(gId);
    nameOverride.set(gId, matches[0].kmzName);
    return;
  }
});

console.log(`\nGnosis matched to existing TSV: ${matchedGnosisIds.size}`);
console.log(`New Gnosis entries to import: ${Object.keys(gnosisEntries).length - matchedGnosisIds.size}`);

// ── 6. Build unified import list ─────────────────────────
// New locations from Gnosis (not in existing TSV from match)
const newLocations = [];
const newSeen = new Set();

Object.keys(gnosisEntries).forEach(gId => {
  if (matchedGnosisIds.has(gId)) return;
  const g = gnosisEntries[gId];

  // Deduplicate within Gnosis itself (by coordinate)
  const ck = coordKey(g.lat, g.lng, 2);
  const dedupKey = `${ck}|${g.name.toLowerCase()}`;
  if (newSeen.has(dedupKey)) return;
  newSeen.add(dedupKey);

  newLocations.push({
    name: g.name,
    lat: g.lat,
    lng: g.lng,
    type: g.type,
    verses: g.verses,
    source: 'gnosis',
    sourceDetail: g.source,
    confidence: g.confidence,
    gnosisId: g.id,
    openbibleId: g.openbibleId,
  });
});

console.log(`New unique locations from Gnosis: ${newLocations.length}`);

// Also export CH entries as reference
console.log(`Church History entries: ${chEntries.length}`);

// ── 7. Write output TSV for import ───────────────────────
const header = 'Name\tLat\tLng\tType\tVerses\tSource\tConfidence\tSourceDetail';
const rows = newLocations.map(l => {
  const versesStr = (l.verses || []).join(',');
  const escapedName = l.name.includes('\t') ? `"${l.name}"` : l.name;
  return [escapedName, l.lat, l.lng, l.type, versesStr, l.source, l.confidence, l.sourceDetail].join('\t');
});

const outputPath = path.join(DATA_DIR, 'gnosis-new.tsv');
fs.writeFileSync(outputPath, header + '\n' + rows.join('\n'), 'utf8');
console.log(`\n✅ Wrote ${newLocations.length} new locations to ${outputPath}`);

// ── 8. Summary ───────────────────────────────────────────
console.log('\n─── MERGE SUMMARY ───');
console.log(`Existing TSV (OpenBible):    ${tsvEntries.length}`);
console.log(`Existing CH:                 ${chEntries.length}`);
console.log(`Total existing:              ${tsvEntries.length + chEntries.length}`);
console.log(`Gnosis total:                ${Object.keys(gnosisEntries).length}`);
console.log(`Gnosis matched to existing:  ${matchedGnosisIds.size}`);
console.log(`New Gnosis to import:        ${newLocations.length}`);
console.log(`Total after merge (est):     ${tsvEntries.length + chEntries.length + newLocations.length}`);

// Type distribution of new locations
const typeCount = {};
newLocations.forEach(l => { typeCount[l.type] = (typeCount[l.type] || 0) + 1; });
console.log('\nType distribution (new):', JSON.stringify(typeCount));

// Sample new locations
console.log('\nSample new locations:');
newLocations.slice(0, 10).forEach(l => console.log(`  ${l.name} (${l.lat}, ${l.lng}) [${l.type}]`));
