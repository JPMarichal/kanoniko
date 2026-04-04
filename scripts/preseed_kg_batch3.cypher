// =====================================================================
// PRE-SEED KG: Known relationships for batch 3 — Church History
// + Didactic Illustration concept node
// Confidence: curated (determined during preparation workflow)
// Run BEFORE indexing to avoid expensive Phase 3 re-discovery
// Date: 2026-04-03
// =====================================================================

// --- DIDACTIC ILLUSTRATION CATEGORY ---
// New concept node for material whose primary value is illustrative:
// anecdotes, real-life stories, metaphors, historical vignettes, etc.

MERGE (a:Entity {name: "Didactic Illustration", type: "concept"})
SET a.aliases = ["Ilustracion Didactica", "Teaching Illustration", "Anecdote", "Story", "Vignette"],
    a.description = "Material whose primary value is illustrative: real stories, anecdotes, metaphors, historical vignettes used to teach gospel principles";

// Sub-types of illustration
MERGE (a:Entity {name: "Historical Vignette", type: "concept"})
MERGE (b:Entity {name: "Didactic Illustration", type: "concept"})
MERGE (a)-[r:IS_A]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Faith Story", type: "concept"})
MERGE (b:Entity {name: "Didactic Illustration", type: "concept"})
MERGE (a)-[r:IS_A]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Biographical Sketch", type: "concept"})
MERGE (b:Entity {name: "Didactic Illustration", type: "concept"})
MERGE (a)-[r:IS_A]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- CHURCH HISTORY TOPICS (encyclopedia) ---

MERGE (a:Entity {name: "Church History Topics", type: "concept"})
SET a.aliases = ["Temas de la historia de la Iglesia"];

MERGE (a:Entity {name: "Church History Topics", type: "concept"})
MERGE (b:Entity {name: "Church History", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Church History Topics", type: "concept"})
MERGE (b:Entity {name: "Historical Vignette", type: "concept"})
MERGE (a)-[r:CONTAINS]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- REVELATIONS IN CONTEXT ---

MERGE (a:Entity {name: "Revelations in Context", type: "concept"})
SET a.aliases = ["Revelaciones en contexto"];

MERGE (a:Entity {name: "Revelations in Context", type: "concept"})
MERGE (b:Entity {name: "Doctrine and Covenants", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Revelations in Context", type: "concept"})
MERGE (b:Entity {name: "Joseph Smith", type: "person"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Revelations in Context", type: "concept"})
MERGE (b:Entity {name: "Historical Vignette", type: "concept"})
MERGE (a)-[r:CONTAINS]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- DAUGHTERS IN MY KINGDOM ---

MERGE (a:Entity {name: "Daughters in My Kingdom", type: "concept"})
SET a.aliases = ["Hijas en Mi reino"];

MERGE (a:Entity {name: "Daughters in My Kingdom", type: "concept"})
MERGE (b:Entity {name: "Relief Society", type: "organization"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Daughters in My Kingdom", type: "concept"})
MERGE (b:Entity {name: "Church History", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Daughters in My Kingdom", type: "concept"})
MERGE (b:Entity {name: "Emma Smith", type: "person"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Daughters in My Kingdom", type: "concept"})
MERGE (b:Entity {name: "Eliza R. Snow", type: "person"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- D&C HISTORICAL RESOURCES 2025 ---

MERGE (a:Entity {name: "D&C Historical Resources 2025", type: "concept"})
MERGE (b:Entity {name: "Doctrine and Covenants", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "D&C Historical Resources 2025", type: "concept"})
MERGE (b:Entity {name: "Biographical Sketch", type: "concept"})
MERGE (a)-[r:CONTAINS]->(b)
SET r += {confidence: "curated", source: "curated_seed", notes: "148 biographical entries"};

MERGE (a:Entity {name: "D&C Historical Resources 2025", type: "concept"})
MERGE (b:Entity {name: "Church History", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- AT THE PULPIT ---

MERGE (a:Entity {name: "At the Pulpit", type: "concept"})
SET a.aliases = ["En el pulpito"];

MERGE (a:Entity {name: "At the Pulpit", type: "concept"})
MERGE (b:Entity {name: "Relief Society", type: "organization"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "At the Pulpit", type: "concept"})
MERGE (b:Entity {name: "Didactic Illustration", type: "concept"})
MERGE (a)-[r:CONTAINS]->(b)
SET r += {confidence: "curated", source: "curated_seed", notes: "61 discourses as teaching illustrations"};

MERGE (a:Entity {name: "Church Historians Press", type: "organization"})
MERGE (b:Entity {name: "At the Pulpit", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- FIRST FIFTY YEARS OF RELIEF SOCIETY ---

MERGE (a:Entity {name: "First Fifty Years of Relief Society", type: "concept"})
MERGE (b:Entity {name: "Relief Society", type: "organization"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Church Historians Press", type: "organization"})
MERGE (b:Entity {name: "First Fifty Years of Relief Society", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "First Fifty Years of Relief Society", type: "concept"})
MERGE (b:Entity {name: "Church History", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- JSP REVELATIONS ---

MERGE (a:Entity {name: "JSP Revelations", type: "concept"})
SET a.aliases = ["Joseph Smiths Revelations"];

MERGE (a:Entity {name: "JSP Revelations", type: "concept"})
MERGE (b:Entity {name: "Doctrine and Covenants", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "JSP Revelations", type: "concept"})
MERGE (b:Entity {name: "Joseph Smith", type: "person"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Church Historians Press", type: "organization"})
MERGE (b:Entity {name: "JSP Revelations", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- GLOBAL HISTORIES ---

MERGE (a:Entity {name: "Global Histories", type: "concept"})
SET a.aliases = ["Historias mundiales"];

MERGE (a:Entity {name: "Global Histories", type: "concept"})
MERGE (b:Entity {name: "Church History", type: "concept"})
MERGE (a)-[r:PART_OF]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Global Histories", type: "concept"})
MERGE (b:Entity {name: "Didactic Illustration", type: "concept"})
MERGE (a)-[r:CONTAINS]->(b)
SET r += {confidence: "curated", source: "curated_seed", notes: "83 countries — faith stories as teaching illustrations"};

MERGE (a:Entity {name: "Global Histories", type: "concept"})
MERGE (b:Entity {name: "Faith Story", type: "concept"})
MERGE (a)-[r:CONTAINS]->(b)
SET r += {confidence: "curated", source: "curated_seed"};
