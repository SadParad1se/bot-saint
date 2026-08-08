from __future__ import annotations

import random
import re
import unicodedata
from typing import NamedTuple
from xml.etree import ElementTree

from maubot import MessageEvent, Plugin
from maubot.handlers import event
from mautrix.types import EventType, MessageType

# BIBLE_FILE = "cze-bkr.zefania.xml"
BIBLE_FILE = "cze-bkr-emoji.xml"

SUPPORTED_MESSAGE_TYPES = frozenset(
    {
        MessageType.TEXT,
        MessageType.NOTICE,
        MessageType.EMOTE,
    }
)

# Deliberately small and auditable. Words are stored without diacritics because
# incoming messages are normalized before matching.
NAUGHTY_WORDS = frozenset(
    {
        # Czech
        "kurva", "kurvy", "kurvě", "kurvu", "kurvou", "kurvám", "kurvách",
        "píča", "píči", "píčo", "píču", "píčou",
        "kunda", "kundy", "kundě", "kundu", "kundou",
        "čurák", "čuráka", "čurákovi", "čurákem", "čuráci",
        "kokot", "kokota", "kokotovi", "kokotem", "kokoti",
        "zmrd", "zmrda", "zmrdovi", "zmrdem", "zmrdi",
        "hajzl", "hajzla", "hajzlovi", "hajzlem", "hajzlové",
        "sráč", "sráče", "sráči", "sráčem",
        "děvka", "děvky", "děvko", "děvku", "děvkou",
        "šlapka", "šlapky", "šlapko", "šlapku",
        "prdel", "prdele", "prdelí",
        "hovno", "hovna", "hovnu", "hovnem",
        "sračka", "sračky", "sračko", "sračku", "sračkou",
        "mrdat", "mrdám", "mrdáš", "mrdá", "mrdal", "mrdala", "mrdání",
        "jebat", "jebu", "jebeš", "jebe", "jebal", "jebání",
        "šukat", "šukám", "šukáš", "šukal", "šukání",
        "posrat", "poser", "posral", "posraný", "posraná", "posrané",
        "zasrat", "zasraný", "zasraná", "zasrané",
        "zkurvit", "zkurvený", "zkurvená", "zkurvené",
        "do prdele", "do píči", "do hajzlu", "do hajzla",
        "kurva fix", "kurva práce", "ty vole",
        "Ježíši Kriste", "Ježíšmarjá", "proboha", "bože", "bože můj",

        # English
        "fuck", "fucking", "fucked", "fucker", "motherfucker", "shit", "shitty",
        "bullshit", "horseshit", "dipshit", "dumbshit", "shithead", "asshole",
        "arsehole", "bitch", "bitchy", "sonofabitch", "goddamn", "hell", "prick",
        "dick", "dickhead", "dickwad", "dickface", "dickhead", "cock", "cocksucker",
        "pussy", "cunt", "twat", "wanker", "bollocks", "bugger", "fuckface",
        "fuckhead", "fuckwit", "fuckwad", "fuckboy", "fucknut", "fuckstick",
        "shitface", "shitbag", "shitstain", "shitshow", "shitfuck", "craphead",
        "douchecanoe", "dickbag", "dickweed", "dicknose", "muppet", "slut",
        "whore", "hoe", "tramp", "scumbag", "sleazebag", "dirtbag", "jackoff",
        "jerkoff", "dumbfuck", "clusterfuck", "mindfuck", "god", "jesus"
    }
)

WORD_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


class Verse(NamedTuple):
    book: str
    chapter: int
    number: int
    text: str


def normalize_words(text: str) -> set[str]:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_diacritics = "".join(
        character for character in decomposed if unicodedata.category(character) != "Mn"
    )
    return set(WORD_PATTERN.findall(without_diacritics))


def contains_naughty_word(text: str) -> bool:
    return not NAUGHTY_WORDS.isdisjoint(normalize_words(text))


def parse_bible(data: bytes) -> tuple[Verse, ...]:
    root = ElementTree.fromstring(data)
    verses: list[Verse] = []

    for book_element in root.findall("BIBLEBOOK"):
        book = book_element.get("bname", "").strip()
        if not book:
            continue

        for chapter_element in book_element.findall("CHAPTER"):
            chapter_value = chapter_element.get("cnumber")
            if not chapter_value:
                continue

            for verse_element in chapter_element.findall("VERS"):
                verse_value = verse_element.get("vnumber")
                text = " ".join("".join(verse_element.itertext()).split())
                if verse_value and text:
                    verses.append(Verse(book, int(chapter_value), int(verse_value), text))

    if not verses:
        raise ValueError("The bundled Bible does not contain any verses")

    return tuple(verses)


def format_verse(verse: Verse) -> str:
    return f"> {verse.text}\n\n— {verse.book} {verse.chapter}:{verse.number} (Bible kralická)"


class SaintBot(Plugin):
    verses: tuple[Verse, ...]

    async def start(self) -> None:
        self.verses = parse_bible(await self.loader.read_file(BIBLE_FILE))
        self.log.info("Loaded %d Czech Bible verses", len(self.verses))

    @event.on(EventType.ROOM_MESSAGE)
    async def check_message(self, evt: MessageEvent) -> None:
        if evt.sender == self.client.mxid:
            return
        if evt.content.msgtype not in SUPPORTED_MESSAGE_TYPES:
            return
        if not contains_naughty_word(evt.content.body):
            return

        await evt.reply(format_verse(random.choice(self.verses)), allow_html=False)


__all__ = ["SaintBot"]
