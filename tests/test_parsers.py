"""Tests for document parsers."""

from pathlib import Path

from alejandria.ingestion.parsers import parse_file


def test_parse_txt(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("Hello world", encoding="utf-8")
    assert parse_file(f) == "Hello world"


def test_parse_markdown(tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Title\n\nSome **bold** text.", encoding="utf-8")
    result = parse_file(f)
    assert "Title" in result
    assert "bold" in result
    assert "<" not in result  # No HTML tags


def test_parse_html(tmp_path: Path) -> None:
    f = tmp_path / "test.html"
    f.write_text("<html><body><h1>Title</h1><p>Content here</p></body></html>", encoding="utf-8")
    result = parse_file(f)
    assert "Title" in result
    assert "Content here" in result
    assert "<" not in result


def test_parse_json(tmp_path: Path) -> None:
    f = tmp_path / "test.json"
    f.write_text('{"title": "Test", "body": "The content"}', encoding="utf-8")
    result = parse_file(f)
    assert "Test" in result
    assert "The content" in result


def test_parse_unsupported(tmp_path: Path) -> None:
    f = tmp_path / "test.xyz"
    f.write_text("data", encoding="utf-8")
    try:
        parse_file(f)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
