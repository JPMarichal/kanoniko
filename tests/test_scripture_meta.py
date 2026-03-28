"""Tests for scripture metadata module."""

import pytest
from alejandria.ingestion.scripture_meta import (
    is_scripture,
    parse_scripture_path,
    parse_verses,
    get_verse_range,
    format_reference,
    build_chunk_reference,
    build_scripture_metadata,
    BOOK_REGISTRY,
)


class TestIsScripture:
    def test_english_bom(self):
        assert is_scripture("en/scriptures/bom/1-nephi/1.txt")

    def test_spanish_bom(self):
        assert is_scripture("es/scriptures/bom/1-nefi/3.txt")

    def test_dc_sections(self):
        assert is_scripture("en/scriptures/dc/sections/76.txt")

    def test_pgp(self):
        assert is_scripture("en/scriptures/pgp/moses/1.txt")

    def test_not_scripture(self):
        assert not is_scripture("en/general-conference/talk.txt")

    def test_not_scripture_root(self):
        assert not is_scripture("readme.txt")

    def test_windows_path(self):
        assert is_scripture("en\\scriptures\\nt\\matthew\\1.txt")


class TestParseScripturePath:
    def test_english_nt(self):
        result = parse_scripture_path("en/scriptures/nt/matthew/1.txt")
        assert result is not None
        assert result["lang"] == "en"
        assert result["volume"] == "nt"
        assert result["book_slug"] == "matthew"
        assert result["chapter_num"] == 1

    def test_spanish_bom(self):
        result = parse_scripture_path("es/scriptures/bom/1-nefi/3.txt")
        assert result is not None
        assert result["lang"] == "es"
        assert result["volume"] == "bom"
        assert result["book_slug"] == "1-nefi"
        assert result["chapter_num"] == 3

    def test_dc_sections(self):
        result = parse_scripture_path("en/scriptures/dc/sections/76.txt")
        assert result is not None
        assert result["volume"] == "dc"
        assert result["book_slug"] is None  # D&C normalizes to None
        assert result["chapter_num"] == 76

    def test_not_scripture(self):
        assert parse_scripture_path("en/manuals/lesson1.txt") is None


class TestParseVerses:
    def test_simple(self):
        text = "1 In the beginning God created.\n2 And the earth was void.\n3 And God said let there be light."
        verses = parse_verses(text)
        assert len(verses) == 3
        assert verses[0] == (1, "In the beginning God created.")
        assert verses[2] == (3, "And God said let there be light.")

    def test_empty(self):
        assert parse_verses("") == []

    def test_no_verses(self):
        assert parse_verses("This is just plain text without verse numbers.") == []

    def test_multiline_verse(self):
        text = "1 First verse starts here\nand continues on next line.\n2 Second verse."
        verses = parse_verses(text)
        assert len(verses) == 2
        assert "continues" in verses[0][1]


class TestGetVerseRange:
    def test_single_verse(self):
        verses = [(1, "Alpha beta gamma"), (2, "Delta epsilon zeta"), (3, "Eta theta iota")]
        chunk = "Delta epsilon zeta"
        result = get_verse_range(chunk, verses)
        assert result == (2, 2)

    def test_range(self):
        verses = [(1, "Alpha beta gamma"), (2, "Delta epsilon zeta"), (3, "Eta theta iota")]
        chunk = "Alpha beta gamma Delta epsilon zeta Eta theta iota"
        result = get_verse_range(chunk, verses)
        assert result == (1, 3)

    def test_no_match(self):
        verses = [(1, "Alpha beta gamma")]
        result = get_verse_range("No matching text here", verses)
        assert result is None


class TestFormatReference:
    def test_english_bom(self):
        ref = format_reference("1-nephi", "bom", 1, 1, 5, "en")
        assert ref == "1 Nephi 1:1-5"

    def test_spanish_bom(self):
        ref = format_reference("1-nephi", "bom", 1, 1, 5, "es")
        assert ref == "1 Nefi 1:1-5"

    def test_single_verse(self):
        ref = format_reference("matthew", "nt", 1, 25, 25, "en")
        assert ref == "Matthew 1:25"

    def test_spanish_nt(self):
        ref = format_reference("matthew", "nt", 1, 25, 25, "es")
        assert ref == "Mateo 1:25"

    def test_dc_english(self):
        ref = format_reference(None, "dc", 76, 22, 24, "en")
        assert ref == "D&C 76:22-24"

    def test_dc_spanish(self):
        ref = format_reference(None, "dc", 76, 22, 24, "es")
        assert ref == "DyC 76:22-24"

    def test_chapter_only(self):
        ref = format_reference("genesis", "ot", 1, lang="en")
        assert ref == "Genesis 1"

    def test_pgp(self):
        ref = format_reference("moses", "pgp", 1, 1, 39, "en")
        assert ref == "Moses 1:1-39"


class TestBuildChunkReference:
    def test_with_verses(self):
        full_text = "1 First verse text here.\n2 Second verse text here.\n3 Third verse."
        chunk = "First verse text here. Second verse text here."
        ref = build_chunk_reference("en/scriptures/bom/1-nephi/1.txt", chunk, full_text)
        assert ref == "1 Nephi 1:1-2"

    def test_not_scripture(self):
        ref = build_chunk_reference("en/manuals/lesson.txt", "some text", "full text")
        assert ref is None


class TestBuildScriptureMetadata:
    def test_scripture_file(self):
        full_text = "1 First verse.\n2 Second verse."
        chunk = "First verse. Second verse."
        meta = build_scripture_metadata("en/scriptures/nt/matthew/1.txt", chunk, full_text)
        assert meta["lang"] == "en"
        assert meta["volume"] == "nt"
        assert meta["book"] == "matthew"
        assert meta["chapter"] == 1
        assert "reference" in meta

    def test_not_scripture(self):
        meta = build_scripture_metadata("en/manuals/lesson.txt", "text", "full")
        assert meta == {}


class TestBookRegistry:
    def test_has_all_bom_books(self):
        bom_books = ["1-nephi", "2-nephi", "jacob", "enos", "jarom", "omni",
                      "words-of-mormon", "mosiah", "alma", "helaman",
                      "3-nephi", "4-nephi", "mormon", "ether", "moroni"]
        for b in bom_books:
            assert b in BOOK_REGISTRY, f"Missing BOM book: {b}"

    def test_has_nt_books(self):
        assert "matthew" in BOOK_REGISTRY
        assert "revelation" in BOOK_REGISTRY

    def test_bilingual(self):
        assert BOOK_REGISTRY["matthew"]["en"] == "Matthew"
        assert BOOK_REGISTRY["matthew"]["es"] == "Mateo"
        assert BOOK_REGISTRY["galatians"]["es"] == "Gálatas"
