"""Tests for textual search."""

from pathlib import Path

from alejandria.search.textual import TextualSearch


def test_index_and_search(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    search = TextualSearch(db_path)

    conn = search.get_connection()
    with conn:
        search.index_chunk(conn, "file1.txt", 0, "Nephi went into the wilderness", 0, 30)
        search.index_chunk(conn, "file1.txt", 1, "He prayed unto the Lord", 31, 55)
        search.index_chunk(conn, "file2.txt", 0, "Faith is the substance of things hoped for", 0, 43)

    results = search.search("Nephi wilderness")
    assert len(results) > 0
    assert results[0].file_path == "file1.txt"


def test_search_empty_query(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    search = TextualSearch(db_path)
    assert search.search("") == []


def test_delete_by_file(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    search = TextualSearch(db_path)

    conn = search.get_connection()
    with conn:
        search.index_chunk(conn, "file1.txt", 0, "First file content", 0, 18)
        search.index_chunk(conn, "file2.txt", 0, "Second file content", 0, 19)

    conn = search.get_connection()
    with conn:
        deleted = search.delete_by_file(conn, "file1.txt")
    assert deleted == 1

    assert search.count_documents() == 1


def test_count(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    search = TextualSearch(db_path)

    assert search.count_chunks() == 0
    assert search.count_documents() == 0

    conn = search.get_connection()
    with conn:
        search.index_chunk(conn, "f.txt", 0, "some text", 0, 9)

    assert search.count_chunks() == 1
    assert search.count_documents() == 1
