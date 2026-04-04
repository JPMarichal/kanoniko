// =====================================================================
// PRE-SEED KG: Known relationships for Project Gutenberg classic works
// Confidence: curated (determined during preparation workflow)
// Run BEFORE indexing to avoid expensive Phase 3 re-discovery
// Date: 2026-04-04
// =====================================================================

// ═══════════════════════════════════════════════════════════════════════
// AUTHORSHIP
// ═══════════════════════════════════════════════════════════════════════

// James E. Talmage — 4 books
MERGE (t:Entity {name: "James E. Talmage", type: "person"})
MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (t)-[r1:AUTHORED]->(aof)
SET r1 += {confidence: "curated", source: "curated_seed", role: "author", source_ref: "Published 1899, commissioned by First Presidency"};

MERGE (t:Entity {name: "James E. Talmage", type: "person"})
MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (t)-[r2:AUTHORED]->(ga)
SET r2 += {confidence: "curated", source: "curated_seed", role: "author", source_ref: "Published 1909, Zion's Printing & Publishing Co."};

MERGE (t:Entity {name: "James E. Talmage", type: "person"})
MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (t)-[r3:AUTHORED]->(hl)
SET r3 += {confidence: "curated", source: "curated_seed", role: "author", source_ref: "Published 1912, first authorized book on LDS temples"};

MERGE (t:Entity {name: "James E. Talmage", type: "person"})
MERGE (vm:Entity {name: "The Vitality of Mormonism", type: "work"})
MERGE (t)-[r4:AUTHORED]->(vm)
SET r4 += {confidence: "curated", source: "curated_seed", role: "author", source_ref: "Published 1919, Boston: Gorham Press"};

// Talmage also authored Jesus the Christ (already in corpus)
MERGE (t:Entity {name: "James E. Talmage", type: "person"})
MERGE (jtc:Entity {name: "Jesus the Christ", type: "work"})
MERGE (t)-[r5:AUTHORED]->(jtc)
SET r5 += {confidence: "curated", source: "curated_seed", role: "author", source_ref: "Published 1915, written in the Salt Lake Temple"};

// Discourses of Brigham Young — BY as speaker, Widtsoe as compiler
MERGE (by:Entity {name: "Brigham Young", type: "person"})
MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (by)-[r6:AUTHORED]->(dby)
SET r6 += {confidence: "curated", source: "curated_seed", role: "speaker", source_ref: "Sermons from Journal of Discourses (1851-1877)"};

MERGE (w:Entity {name: "John A. Widtsoe", type: "person"})
MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (w)-[r7:AUTHORED]->(dby)
SET r7 += {confidence: "curated", source: "curated_seed", role: "compiler", source_ref: "Compiled 1925, thematic arrangement from JD"};

// ═══════════════════════════════════════════════════════════════════════
// CALLING / ROLE AT TIME OF WRITING
// ═══════════════════════════════════════════════════════════════════════

MERGE (t:Entity {name: "James E. Talmage", type: "person"})
MERGE (q12:Entity {name: "Quorum of the Twelve Apostles", type: "organization"})
MERGE (t)-[r8:CALLED_AS]->(q12)
SET r8 += {confidence: "curated", source: "curated_seed", source_ref: "Ordained apostle December 8, 1911"};

MERGE (w:Entity {name: "John A. Widtsoe", type: "person"})
MERGE (q12:Entity {name: "Quorum of the Twelve Apostles", type: "organization"})
MERGE (w)-[r9:CALLED_AS]->(q12)
SET r9 += {confidence: "curated", source: "curated_seed", source_ref: "Ordained apostle January 17, 1921"};

MERGE (by:Entity {name: "Brigham Young", type: "person"})
MERGE (pres:Entity {name: "President of the Church", type: "concept"})
MERGE (by)-[r10:CALLED_AS]->(pres)
SET r10 += {confidence: "curated", source: "curated_seed", source_ref: "Sustained December 27, 1847"};

// ═══════════════════════════════════════════════════════════════════════
// SOURCE RELATIONSHIPS
// ═══════════════════════════════════════════════════════════════════════

// Discourses of BY compiled from Journal of Discourses
MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (jd:Entity {name: "Journal of Discourses", type: "work"})
MERGE (dby)-[r11:CITES]->(jd)
SET r11 += {confidence: "curated", source: "curated_seed", source_ref: "Primary source: 26 volumes of JD (1854-1886)"};

// ═══════════════════════════════════════════════════════════════════════
// CROSS-REFERENCES BETWEEN TALMAGE WORKS
// ═══════════════════════════════════════════════════════════════════════

// AoF references other Talmage works
MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (jtc:Entity {name: "Jesus the Christ", type: "work"})
MERGE (aof)-[r12:CITES]->(jtc)
SET r12 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (aof)-[r13:CITES]->(ga)
SET r13 += {confidence: "curated", source: "curated_seed"};

// House of the Lord references Articles of Faith
MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (hl)-[r14:CITES]->(aof)
SET r14 += {confidence: "curated", source: "curated_seed"};

// ═══════════════════════════════════════════════════════════════════════
// KEY DOCTRINAL TOPICS (COVERS relation)
// ═══════════════════════════════════════════════════════════════════════

// Articles of Faith — systematic theology
MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c1:Entity {name: "Godhead", type: "concept"})
MERGE (aof)-[r15:COVERS]->(c1)
SET r15 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c2:Entity {name: "Atonement", type: "concept"})
MERGE (aof)-[r16:COVERS]->(c2)
SET r16 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c3:Entity {name: "Baptism", type: "concept"})
MERGE (aof)-[r17:COVERS]->(c3)
SET r17 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c4:Entity {name: "Holy Ghost", type: "concept"})
MERGE (aof)-[r18:COVERS]->(c4)
SET r18 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c5:Entity {name: "Priesthood", type: "concept"})
MERGE (aof)-[r19:COVERS]->(c5)
SET r19 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c6:Entity {name: "Book of Mormon", type: "scripture"})
MERGE (aof)-[r20:COVERS]->(c6)
SET r20 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c7:Entity {name: "Resurrection", type: "concept"})
MERGE (aof)-[r21:COVERS]->(c7)
SET r21 += {confidence: "curated", source: "curated_seed"};

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (c8:Entity {name: "Gathering of Israel", type: "concept"})
MERGE (aof)-[r22:COVERS]->(c8)
SET r22 += {confidence: "curated", source: "curated_seed"};

// Great Apostasy — apostasy and restoration
MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (c9:Entity {name: "Apostasy", type: "concept"})
MERGE (ga)-[r23:COVERS]->(c9)
SET r23 += {confidence: "curated", source: "curated_seed"};

MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (c10:Entity {name: "Restoration", type: "concept"})
MERGE (ga)-[r24:COVERS]->(c10)
SET r24 += {confidence: "curated", source: "curated_seed"};

MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (c5:Entity {name: "Priesthood", type: "concept"})
MERGE (ga)-[r25:COVERS]->(c5)
SET r25 += {confidence: "curated", source: "curated_seed"};

// House of the Lord — temples
MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (c11:Entity {name: "Temple", type: "concept"})
MERGE (hl)-[r26:COVERS]->(c11)
SET r26 += {confidence: "curated", source: "curated_seed"};

MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (c12:Entity {name: "Endowment", type: "concept"})
MERGE (hl)-[r27:COVERS]->(c12)
SET r27 += {confidence: "curated", source: "curated_seed"};

MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (c13:Entity {name: "Baptism for the Dead", type: "concept"})
MERGE (hl)-[r28:COVERS]->(c13)
SET r28 += {confidence: "curated", source: "curated_seed"};

MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (c14:Entity {name: "Salt Lake Temple", type: "place"})
MERGE (hl)-[r29:COVERS]->(c14)
SET r29 += {confidence: "curated", source: "curated_seed"};

// Discourses of BY — broad doctrinal coverage
MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (c1:Entity {name: "Godhead", type: "concept"})
MERGE (dby)-[r30:COVERS]->(c1)
SET r30 += {confidence: "curated", source: "curated_seed"};

MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (c5:Entity {name: "Priesthood", type: "concept"})
MERGE (dby)-[r31:COVERS]->(c5)
SET r31 += {confidence: "curated", source: "curated_seed"};

MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (c15:Entity {name: "United Order", type: "concept"})
MERGE (dby)-[r32:COVERS]->(c15)
SET r32 += {confidence: "curated", source: "curated_seed"};

MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
MERGE (c16:Entity {name: "Pioneer era", type: "period"})
MERGE (dby)-[r33:COVERS]->(c16)
SET r33 += {confidence: "curated", source: "curated_seed"};

// ═══════════════════════════════════════════════════════════════════════
// TEMPORAL — publication dates
// ═══════════════════════════════════════════════════════════════════════

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
SET aof.date = "1899", aof.aliases = ["Articles of Faith", "AoF"];

MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
SET ga.date = "1909", ga.aliases = ["Great Apostasy"];

MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
SET hl.date = "1912", hl.aliases = ["House of the Lord"];

MERGE (vm:Entity {name: "The Vitality of Mormonism", type: "work"})
SET vm.date = "1919", vm.aliases = ["Vitality of Mormonism"];

MERGE (dby:Entity {name: "Discourses of Brigham Young", type: "work"})
SET dby.date = "1925", dby.aliases = ["Discourses of BY", "DBY"];

// ═══════════════════════════════════════════════════════════════════════
// SUCCESSION — Talmage works in chronological order
// ═══════════════════════════════════════════════════════════════════════

MERGE (aof:Entity {name: "The Articles of Faith", type: "work"})
MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (aof)-[r34:PRECEDED_BY {confidence: "curated", source: "curated_seed"}]->(ga);

MERGE (ga:Entity {name: "The Great Apostasy", type: "work"})
MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (ga)-[r35:PRECEDED_BY {confidence: "curated", source: "curated_seed"}]->(hl);

MERGE (hl:Entity {name: "The House of the Lord", type: "work"})
MERGE (jtc:Entity {name: "Jesus the Christ", type: "work"})
MERGE (hl)-[r36:PRECEDED_BY {confidence: "curated", source: "curated_seed"}]->(jtc);

MERGE (jtc:Entity {name: "Jesus the Christ", type: "work"})
MERGE (vm:Entity {name: "The Vitality of Mormonism", type: "work"})
MERGE (jtc)-[r37:PRECEDED_BY {confidence: "curated", source: "curated_seed"}]->(vm);
