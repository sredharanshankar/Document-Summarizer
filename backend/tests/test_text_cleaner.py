from app.services.text_cleaner import clean_pages


def test_collapses_repeated_whitespace() -> None:
    result = clean_pages(["This   has     extra    spaces."])
    assert result == "This has extra spaces."


def test_dehyphenates_wrapped_words() -> None:
    result = clean_pages(["This is a docu-\nment about testing."])
    assert "document about testing" in result
    assert "docu-" not in result


def test_rejoins_mid_paragraph_linebreaks_but_keeps_paragraph_breaks() -> None:
    result = clean_pages(["First line\nsecond line\n\nNew paragraph here."])
    assert result == "First line second line\n\nNew paragraph here."


def test_strips_repeated_headers_and_footers_across_pages() -> None:
    pages = [
        "CONFIDENTIAL REPORT\nContent for page one goes here.\nPage 1",
        "CONFIDENTIAL REPORT\nContent for page two goes here.\nPage 2",
        "CONFIDENTIAL REPORT\nContent for page three goes here.\nPage 3",
        "CONFIDENTIAL REPORT\nContent for page four goes here.\nPage 4",
    ]
    result = clean_pages(pages)
    assert result.count("CONFIDENTIAL REPORT") == 0
    assert "Content for page one goes here." in result
    assert "Content for page four goes here." in result


def test_does_not_strip_boundary_lines_when_not_repeated() -> None:
    pages = [
        "Introduction\nSome unique content.",
        "Methodology\nOther unique content.",
        "Results\nMore unique content.",
    ]
    result = clean_pages(pages)
    assert "Introduction" in result
    assert "Methodology" in result


def test_normalizes_unicode() -> None:
    # "ﬁ" (U+FB01, ligature) should normalize to "fi"
    result = clean_pages(["This is a ﬁle."])
    assert "file." in result


def test_drops_empty_pages() -> None:
    result = clean_pages(["Real content here.", "   \n  ", ""])
    assert result == "Real content here."
