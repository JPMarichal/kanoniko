// =====================================================================
// PRE-SEED KG: Known relationships for supplementary corpus material
// Confidence: curated (determined during preparation workflow)
// Run BEFORE indexing to avoid expensive Phase 3 re-discovery
// Date: 2026-04-03
// =====================================================================

// --- AUTHORSHIP ---

// PMG 2nd ed. (2023): First Presidency + Q12
MERGE (a:Entity {name: "First Presidency", type: "organization"})
MERGE (b:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "author"};

MERGE (a:Entity {name: "Quorum of the Twelve Apostles", type: "organization"})
MERGE (b:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "author"};

// Charted Course: J. Reuben Clark Jr. (1938)
MERGE (a:Entity {name: "J. Reuben Clark Jr.", type: "person"})
MERGE (b:Entity {name: "The Charted Course of the Church in Education", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "author", source_ref: "1938 address to S&I"};

// Teaching in the Savior's Way: First Presidency
MERGE (a:Entity {name: "First Presidency", type: "organization"})
MERGE (b:Entity {name: "Teaching in the Savior's Way", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "compiler"};

// Leadership Instruction: First Presidency
MERGE (a:Entity {name: "First Presidency", type: "organization"})
MERGE (b:Entity {name: "Leadership Instruction", type: "concept"})
MERGE (a)-[r:AUTHORED]->(b)
SET r += {confidence: "curated", source: "curated_seed", role: "compiler"};

// --- DOCTRINAL TEACHINGS (PMG Lessons -> Core Doctrines) ---

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Restoration", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Plan of Salvation", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Faith", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Repentance", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Baptism", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Priesthood", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- TEACHING PAMPHLETS -> Core Doctrines ---

MERGE (a:Entity {name: "Restoration Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Restoration", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Plan of Salvation Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Plan of Salvation", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Gospel of Jesus Christ Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Faith", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Gospel of Jesus Christ Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Repentance", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Gospel of Jesus Christ Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Baptism", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Chastity Pamphlet", type: "concept"})
MERGE (b:Entity {name: "The Law of Chastity", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Word of Wisdom Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Word of Wisdom", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Tithing and Fast Offerings Pamphlet", type: "concept"})
MERGE (b:Entity {name: "Tithing", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- CROSS-REFERENCES (PMG <-> Pamphlets) ---

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Restoration Pamphlet", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Plan of Salvation Pamphlet", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "Gospel of Jesus Christ Pamphlet", type: "concept"})
MERGE (a)-[r:REFERENCES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- ORGANIZATIONAL STRUCTURE ---

MERGE (a:Entity {name: "Bishop", type: "calling"})
MERGE (b:Entity {name: "Bishopric", type: "organization"})
MERGE (a)-[r:PRESIDES_OVER]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Relief Society President", type: "calling"})
MERGE (b:Entity {name: "Relief Society", type: "organization"})
MERGE (a)-[r:PRESIDES_OVER]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// Counseling Resources: primary tool for bishops
MERGE (a:Entity {name: "Counseling Resources", type: "concept"})
SET a.aliases = ["Recursos para orientar"];

MERGE (a:Entity {name: "Bishop", type: "calling"})
MERGE (b:Entity {name: "Counseling Resources", type: "concept"})
MERGE (a)-[r:USES]->(b)
SET r += {confidence: "curated", source: "curated_seed", source_ref: "Primary audience: bishops and stake presidents"};

// --- TEMPORAL ---

MERGE (a:Entity {name: "The Charted Course of the Church in Education", type: "concept"})
MERGE (b:Entity {name: "1938", type: "period"})
MERGE (a)-[r:DATED_TO]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (b:Entity {name: "2023", type: "period"})
MERGE (a)-[r:DATED_TO]->(b)
SET r += {confidence: "curated", source: "curated_seed", source_ref: "2nd edition"};

// --- S&I: Charted Course foundational role ---

MERGE (a:Entity {name: "The Charted Course of the Church in Education", type: "concept"})
MERGE (b:Entity {name: "Seminaries and Institutes", type: "organization"})
MERGE (a)-[r:FOUNDATIONAL_FOR]->(b)
SET r += {confidence: "curated", source: "curated_seed", source_ref: "Defines S&I teaching philosophy since 1938"};

// --- Leadership Instruction: aliases ---

MERGE (li:Entity {name: "Leadership Instruction", type: "concept"})
SET li.aliases = ["Instruccion a los lideres"];

// --- Old Testament Stories: aliases ---

MERGE (ot:Entity {name: "Old Testament Stories", type: "concept"})
SET ot.aliases = ["Historias del Antiguo Testamento"];

// --- OT Stories -> Key biblical figures ---

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Adam", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Abraham", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Moses", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "David", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Elijah", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Daniel", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Esther", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Noah", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Joseph", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

MERGE (a:Entity {name: "Old Testament Stories", type: "concept"})
MERGE (b:Entity {name: "Isaiah", type: "person"})
MERGE (a)-[r:TEACHES_ABOUT]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- Teaching in the Savior's Way -> Teaching concepts ---

MERGE (a:Entity {name: "Teaching in the Savior's Way", type: "concept"})
MERGE (b:Entity {name: "Teaching by the Spirit", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed"};

// --- PMG -> Missionary concepts ---

MERGE (mc:Entity {name: "Missionary Work", type: "concept"})
MERGE (a:Entity {name: "Preach My Gospel", type: "concept"})
MERGE (a)-[r:TEACHES]->(mc)
SET r += {confidence: "curated", source: "curated_seed"};

// --- On Holy Ground -> Historic Sites ---

MERGE (ohg:Entity {name: "On Holy Ground", type: "concept"})
MERGE (a:Entity {name: "On Holy Ground", type: "concept"})
MERGE (b:Entity {name: "Missionary Work", type: "concept"})
MERGE (a)-[r:TEACHES]->(b)
SET r += {confidence: "curated", source: "curated_seed", source_ref: "Historic-site missionary teaching"};
