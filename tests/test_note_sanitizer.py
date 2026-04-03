"""Tests for conference note sanitization and structured parsing."""

import pytest
from alejandria.knowledge.note_sanitizer import (
    ParsedNote,
    parse_note,
    parse_notes,
    extract_note_relations,
    _clean_author_name,
    _strip_attribution_garbage,
)


class TestParseNote:
    """Test individual note parsing and classification."""

    def test_pure_scripture(self):
        note = parse_note("1.  Matthew 23:27 .")
        assert note.note_type == "scripture"
        assert note.note_index == 1
        assert len(note.scripture_refs) >= 1

    def test_pure_scripture_spanish(self):
        note = parse_note("2.  Mosíah 2:41.")
        assert note.note_type == "scripture"

    def test_see_scripture(self):
        note = parse_note("4.  See 2 Ne. 9:13 ; Alma 34:9 ; Abr. 3:22–27 .")
        assert note.note_type == "scripture"
        assert len(note.scripture_refs) >= 2

    def test_vease_scripture(self):
        note = parse_note("4.  Véase Artículos de Fe 1:3 .")
        assert note.note_type == "scripture"

    def test_talk_reference_ensign(self):
        note = parse_note(
            '6.  Dallin H. Oaks, "Preparation for the Second Coming," '
            "Ensign or Liahona, May 2004, 9."
        )
        assert note.note_type == "talk_ref"
        assert note.cited_author == "Dallin H. Oaks"
        assert note.cited_title == "Preparation for the Second Coming"
        assert note.cited_publication == "Ensign or Liahona"

    def test_talk_reference_with_elder_prefix(self):
        note = parse_note(
            '2.  See Russell M. Nelson, "The Magnificence of Man," '
            "Ensign, Jan. 1988, 64–69."
        )
        assert note.note_type == "talk_ref"
        assert note.cited_author == "Russell M. Nelson"
        assert note.cited_title == "The Magnificence of Man"

    def test_conference_report_reference(self):
        note = parse_note(
            "7.  In Conference Report, Apr. 1979, 77; or Ensign, May 1979, 53."
        )
        assert note.note_type == "talk_ref"
        assert note.cited_publication == "Conference Report"
        assert "Apr. 1979" in note.cited_date

    def test_conference_report_with_title(self):
        note = parse_note(
            '11. "Our Brothers\' Keepers," Ensign, June 1998, 33, 38.'
        )
        assert note.note_type == "talk_ref"
        assert note.cited_title == "Our Brothers' Keepers"

    def test_hymn_reference(self):
        note = parse_note(
            '21. "How Great the Wisdom and the Love," Hymns, no. 195.'
        )
        assert note.note_type == "hymn_ref"
        assert note.cited_title == "How Great the Wisdom and the Love"

    def test_hymn_reference_spanish(self):
        note = parse_note(
            '3.  "Ven, sígueme", Himnos, 116.'
        )
        assert note.note_type == "hymn_ref"
        assert "Ven, sígueme" in note.cited_title

    def test_guide_to_scriptures(self):
        note = parse_note(
            '2.  See Guide to the Scriptures, "Kingdom of God or Kingdom of Heaven," '
            "Gospel Library."
        )
        assert note.note_type == "guide_ref"
        assert note.concept_name == "Kingdom of God or Kingdom of Heaven"

    def test_guia_escrituras_spanish(self):
        note = parse_note(
            '5.  Véase Guía de las Escrituras, "Arrepentimiento".'
        )
        assert note.note_type == "guide_ref"
        assert note.concept_name == "Arrepentimiento"

    def test_teachings_compilation(self):
        note = parse_note(
            "3.  See Teachings of the Prophet Joseph Smith, "
            "sel. Joseph Fielding Smith (1976), 349–50."
        )
        assert note.note_type == "book_ref"
        assert "Joseph Smith" in note.cited_title or "Joseph Smith" in note.cited_author

    def test_book_reference(self):
        note = parse_note(
            "7.  See Andrew Karl Larson, The Red Hills of November (1957), 311–13."
        )
        assert note.note_type == "book_ref"
        assert note.cited_date == "1957"

    def test_note_index_extraction(self):
        note = parse_note("15.  Some note text.")
        assert note.note_index == 15

    def test_empty_note(self):
        note = parse_note("")
        assert note.note_type == "other"
        assert note.raw_text == ""


class TestCleanAuthorName:
    """Test author name cleaning."""

    def test_strip_president(self):
        assert _clean_author_name("President Russell M. Nelson") == "Russell M. Nelson"

    def test_strip_elder(self):
        assert _clean_author_name("Elder Dallin H. Oaks") == "Dallin H. Oaks"

    def test_strip_sister(self):
        assert _clean_author_name("Sister Amy A. Wright") == "Amy A. Wright"

    def test_strip_calling_concat(self):
        result = _clean_author_name("Russell M. NelsonOf the Quorum")
        assert result == "Russell M. Nelson"

    def test_no_prefix(self):
        assert _clean_author_name("Gordon B. Hinckley") == "Gordon B. Hinckley"


class TestStripAttributionGarbage:
    """Test garbage pattern removal."""

    def test_name_calling_concat(self):
        text = "Russell M. NelsonOf the Quorum of the Twelve Apostles"
        result = _strip_attribution_garbage(text)
        assert "Of the Quorum" not in result

    def test_cuorum_spanish(self):
        text = "Del Cuórum de los Doce Apóstoles"
        result = _strip_attribution_garbage(text)
        assert "Cuórum" not in result

    def test_preserves_normal_text(self):
        text = "The Savior taught about repentance and faith."
        result = _strip_attribution_garbage(text)
        assert result == text


class TestExtractNoteRelations:
    """Test full relation extraction from note lists."""

    def test_talk_crossref_creates_references_relation(self):
        notes = [
            '6.  Dallin H. Oaks, "Preparation for the Second Coming," '
            "Ensign or Liahona, May 2004, 9.",
        ]
        entities, relations = extract_note_relations("My Talk Title", notes)

        # Should create talk entity for cited talk
        talk_ents = [e for e in entities if e["type"] == "talk"]
        assert any(e["name"] == "Preparation for the Second Coming" for e in talk_ents)

        # Should create person entity for cited author
        person_ents = [e for e in entities if e["type"] == "person"]
        assert any(e["name"] == "Dallin H. Oaks" for e in person_ents)

        # Should create REFERENCES relation
        ref_rels = [r for r in relations if r["rel_type"] == "REFERENCES"]
        assert len(ref_rels) >= 1
        assert ref_rels[0]["from_name"] == "My Talk Title"
        assert ref_rels[0]["to_name"] == "Preparation for the Second Coming"
        assert ref_rels[0]["props"]["confidence"] == "note_reference"

    def test_hymn_creates_cites_relation(self):
        notes = [
            '21. "How Great the Wisdom and the Love," Hymns, no. 195.',
        ]
        entities, relations = extract_note_relations("My Talk", notes)

        hymn_ents = [e for e in entities if e["type"] == "hymn"]
        assert any(e["name"] == "How Great the Wisdom and the Love" for e in hymn_ents)

        cites = [r for r in relations if r["rel_type"] == "CITES"]
        assert len(cites) >= 1

    def test_guide_creates_discusses_relation(self):
        notes = [
            '2.  See Guide to the Scriptures, "Repentance," Gospel Library.',
        ]
        entities, relations = extract_note_relations("My Talk", notes)

        concepts = [e for e in entities if e["type"] == "concept"]
        assert any(e["name"] == "Repentance" for e in concepts)

        discusses = [r for r in relations if r["rel_type"] == "DISCUSSES"]
        assert len(discusses) >= 1

    def test_scripture_only_no_extra_entities(self):
        notes = ["1.  Matthew 23:27 ."]
        entities, relations = extract_note_relations("My Talk", notes)
        # Scripture notes don't create new entities (handled by CITES in pipeline)
        assert len(entities) == 0
        assert len(relations) == 0

    def test_mixed_notes(self):
        notes = [
            "1.  Matthew 23:27 .",
            '6.  Dallin H. Oaks, "Faith in the Lord Jesus Christ," Ensign, May 1994, 99.',
            '21. "How Great the Wisdom and the Love," Hymns, no. 195.',
        ]
        entities, relations = extract_note_relations("My Talk", notes)
        # Should have talk + person + hymn entities
        types = {e["type"] for e in entities}
        assert "talk" in types
        assert "person" in types
        assert "hymn" in types

    def test_deduplication(self):
        notes = [
            '2.  Russell M. Nelson, "Talk One," Ensign, May 2020, 1.',
            '5.  Russell M. Nelson, "Talk Two," Ensign, Oct. 2020, 5.',
        ]
        entities, relations = extract_note_relations("My Talk", notes)
        # Russell M. Nelson should appear only once
        person_ents = [e for e in entities if e["type"] == "person" and e["name"] == "Russell M. Nelson"]
        assert len(person_ents) == 1
