// =====================================================================
// PRE-SEED KG: Known relationships for batch 2 corpus material
// Confidence: curated (determined during preparation workflow)
// Run BEFORE indexing to avoid expensive Phase 3 re-discovery
// Date: 2026-04-03
// =====================================================================

// --- TEMPLE PREPARATION MANUALS ---

MERGE (a:Entity {name: "Preparing to Enter the Holy Temple", type: "concept"})
MERGE (b:Entity {name: "Temple Covenants", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preparing to Enter the Holy Temple", type: "concept"})
MERGE (b:Entity {name: "Endowment", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preparing to Enter the Holy Temple", type: "concept"})
MERGE (b:Entity {name: "Plan of Salvation", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Endowed from on High", type: "concept"})
MERGE (b:Entity {name: "Temple Ordinances", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Endowed from on High", type: "concept"})
MERGE (b:Entity {name: "Sealing", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Endowed from on High", type: "concept"})
MERGE (b:Entity {name: "Worthiness", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// Temple Preparation curriculum grouping
MERGE (a:Entity {name: "Preparing to Enter the Holy Temple", type: "concept"})
MERGE (b:Entity {name: "Temple Preparation", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Endowed from on High", type: "concept"})
MERGE (b:Entity {name: "Temple Preparation", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// Authorship
MERGE (a:Entity {name: "Church Correlation", type: "organization"})
MERGE (b:Entity {name: "Preparing to Enter the Holy Temple", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "producer"};

MERGE (a:Entity {name: "Church Correlation", type: "organization"})
MERGE (b:Entity {name: "Endowed from on High", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "producer"};

// --- SCRIPTURE HELPS ---

MERGE (a:Entity {name: "Scripture Helps: Old Testament", type: "concept"})
MERGE (b:Entity {name: "Old Testament", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Scripture Helps: New Testament", type: "concept"})
MERGE (b:Entity {name: "New Testament", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Scripture Helps: Old Testament", type: "concept"})
MERGE (b:Entity {name: "Scripture Study", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Scripture Helps: New Testament", type: "concept"})
MERGE (b:Entity {name: "Scripture Study", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- LEARNING FROM GENERAL CONFERENCE ---

MERGE (a:Entity {name: "Learning from General Conference", type: "concept"})
MERGE (b:Entity {name: "General Conference", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Learning from General Conference", type: "concept"})
MERGE (b:Entity {name: "Teaching Methods", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Relief Society", type: "organization"})
MERGE (b:Entity {name: "Learning from General Conference", type: "concept"})
MERGE (a)-[r:USES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Elders Quorum", type: "organization"})
MERGE (b:Entity {name: "Learning from General Conference", type: "concept"})
MERGE (a)-[r:USES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- ABOUT THE HYMNS ---

MERGE (a:Entity {name: "About the Hymns", type: "concept"})
MERGE (b:Entity {name: "Sacred Music", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "About the Hymns", type: "concept"})
MERGE (b:Entity {name: "Worship", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "About the Hymns", type: "concept"})
MERGE (b:Entity {name: "Hymns for Home and Church", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- SELF-RELIANCE COURSES ---

// Initiative grouping
MERGE (sr:Entity {name: "Self-Reliance Initiative", type: "concept"})
SET sr.aliases = ["Iniciativa de Autosuficiencia"];

MERGE (a:Entity {name: "Personal Finances", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Starting a Business", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Find a Better Job", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Education for Better Work", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Emotional Resilience", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "My Foundation", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// Authorship
MERGE (a:Entity {name: "Self-Reliance Services", type: "organization"})
MERGE (b:Entity {name: "Self-Reliance Initiative", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "producer"};

// Key TEACHES relationships per course
MERGE (a:Entity {name: "Personal Finances", type: "concept"})
MERGE (b:Entity {name: "Tithing", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Personal Finances", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Starting a Business", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Find a Better Job", type: "concept"})
MERGE (b:Entity {name: "Self-Reliance", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Education for Better Work", type: "concept"})
MERGE (b:Entity {name: "Education", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Emotional Resilience", type: "concept"})
MERGE (b:Entity {name: "Emotional Health", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Emotional Resilience", type: "concept"})
MERGE (b:Entity {name: "Atonement of Jesus Christ", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "My Foundation", type: "concept"})
MERGE (b:Entity {name: "Faith", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- MARRIAGE AND FAMILY RELATIONS ---

MERGE (a:Entity {name: "Marriage and Family Relations", type: "concept"})
MERGE (b:Entity {name: "Marriage", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Marriage and Family Relations", type: "concept"})
MERGE (b:Entity {name: "Family", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Marriage and Family Relations", type: "concept"})
MERGE (b:Entity {name: "The Family: A Proclamation to the World", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- MUSLIMS AND LATTER-DAY SAINTS ---

MERGE (a:Entity {name: "Muslims and Latter-day Saints", type: "concept"})
MERGE (b:Entity {name: "Interfaith Dialogue", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Muslims and Latter-day Saints", type: "concept"})
MERGE (b:Entity {name: "Islam", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Muslims and Latter-day Saints", type: "concept"})
MERGE (b:Entity {name: "Abrahamic Covenant", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- RELIGIOUS FREEDOM ---

MERGE (a:Entity {name: "Religious Freedom", type: "concept"})
MERGE (b:Entity {name: "Religious Liberty", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Religious Freedom", type: "concept"})
MERGE (b:Entity {name: "Civic Engagement", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- SUCCEED IN SCHOOL ---

MERGE (a:Entity {name: "Succeed in School", type: "concept"})
MERGE (b:Entity {name: "Education", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Succeed in School", type: "concept"})
MERGE (b:Entity {name: "Youth", type: "concept"})
MERGE (a)-[r:AUDIENCE]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- SCRIPTURE STUDY SKILLS & CHRISTLIKE TEACHING ---

MERGE (a:Entity {name: "Scripture Study Skills", type: "concept"})
MERGE (b:Entity {name: "Scripture Study", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Principles of Christlike Teaching", type: "concept"})
MERGE (b:Entity {name: "Teaching Methods", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Principles of Christlike Teaching", type: "concept"})
MERGE (b:Entity {name: "Teaching by the Spirit", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};
