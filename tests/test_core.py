from __future__ import annotations

import pytest

from sadparad1se_bot_saint import (
    Verse,
    contains_naughty_word,
    format_verse,
    normalize_words,
    parse_bible,
)


@pytest.mark.parametrize(
    "message",
    [
        "Ty jsi ale kUrVa!",
        "Do PÍČI.",
        "To je pekna sracka.",
        "What the fuck?",
        "This is bullshit!",
    ],
)
def test_detects_czech_and_english_words(message: str) -> None:
    assert contains_naughty_word(message)


@pytest.mark.parametrize(
    "message",
    [
        "Křik se ozval z dálky.",
        "Přečetl jsem krátký úryvek.",
        "Můj synovec přijede zítra.",
        "Pass the assignment to the assistant.",
        "The classic tale is unfinished.",
    ],
)
def test_ordinary_words_do_not_match(message: str) -> None:
    assert not contains_naughty_word(message)


def test_normalization_ignores_case_and_diacritics() -> None:
    assert normalize_words("PÍČA píča PiCa") == {"pica"}


def test_parse_bible_and_format_verse() -> None:
    data = b"""\
    <XMLBIBLE>
      <BIBLEBOOK bname="Jan">
        <CHAPTER cnumber="3">
          <VERS vnumber="16">Nebo tak B&uring;h miloval sv&ecaron;t.</VERS>
        </CHAPTER>
      </BIBLEBOOK>
    </XMLBIBLE>
    """.replace(b"&uring;", "ů".encode()).replace(b"&ecaron;", "ě".encode())

    assert parse_bible(data) == (Verse("Jan", 3, 16, "Nebo tak Bůh miloval svět."),)
    assert format_verse(parse_bible(data)[0]) == (
        "> Nebo tak Bůh miloval svět.\n\n— Jan 3:16 (Bible kralická)"
    )


def test_parse_bible_rejects_empty_data() -> None:
    with pytest.raises(ValueError, match="does not contain any verses"):
        parse_bible(b"<XMLBIBLE />")
