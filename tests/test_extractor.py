"""Tests for the knowledge graph extractor."""

from alejandria.knowledge.extractor import KGExtractor


def test_extract_persons() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Nephi went forth into the wilderness with his brother Laman.")
    names = {e.name for e in result.entities}
    assert "Nephi" in names
    assert "Laman" in names


def test_extract_places() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Lehi dwelt at Jerusalem in all his days.")
    names = {e.name for e in result.entities}
    assert "Lehi" in names
    assert "Jerusalem" in names


def test_extract_concepts() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Through faith and repentance we can receive the Atonement.")
    names = {e.name for e in result.entities}
    assert "Faith" in names
    assert "Repentance" in names
    assert "Atonement" in names


def test_extract_peoples() -> None:
    extractor = KGExtractor()
    result = extractor.extract("The Nephites fought against the Lamanites.")
    names = {e.name for e in result.entities}
    assert "Nephites" in names
    assert "Lamanites" in names


def test_extract_objects() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Lehi found the Liahona and the sword of Laban was preserved.")
    names = {e.name for e in result.entities}
    assert "Liahona" in names


def test_extract_scripture_references() -> None:
    extractor = KGExtractor()
    result = extractor.extract("As stated in 1 Nephi 3:7 and Alma 32:21, we must have faith.")
    assert len(result.scripture_refs) >= 2
    refs = result.scripture_refs
    assert any("1 Nephi 3:7" in r for r in refs)
    assert any("Alma 32:21" in r for r in refs)


def test_extract_bilingual() -> None:
    """Test that Spanish aliases are recognized."""
    extractor = KGExtractor()
    result = extractor.extract("Nefi oró al Señor en Jerusalén por fe y arrepentimiento.")
    names = {e.name for e in result.entities}
    # "Nefi" -> Nephi, "Jerusalén" -> Jerusalem, "fe" -> Faith, "arrepentimiento" -> Repentance
    assert "Nephi" in names
    assert "Jerusalem" in names
    assert "Faith" in names
    assert "Repentance" in names


def test_extract_relations() -> None:
    extractor = KGExtractor()
    result = extractor.extract("Nephi traveled to Jerusalem to get the brass plates.")
    assert len(result.relations) > 0
    # Should have person-place and person-object relations
    rel_types = {r.relation for r in result.relations}
    assert len(rel_types) > 0


def test_extract_empty_text() -> None:
    extractor = KGExtractor()
    result = extractor.extract("")
    assert result.entities == []
    assert result.relations == []
    assert result.scripture_refs == []


def test_extract_no_entities() -> None:
    extractor = KGExtractor()
    result = extractor.extract("The weather was nice today and I went for a walk.")
    assert len(result.entities) == 0
