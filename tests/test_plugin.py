from __future__ import annotations

from unittest.mock import patch

import pytest
from mautrix.types import MessageType

from sadparad1se_bot_saint import Verse


async def test_profanity_gets_one_random_verse_reply(maubot_plugin, maubot_test_bot) -> None:
    verse = Verse("Jan", 3, 16, "Nebo tak Bůh miloval svět.")
    maubot_plugin.verses = (verse,)

    with patch("sadparad1se_bot_saint.random.choice", return_value=verse) as choose:
        await maubot_test_bot.send("Kurva, fuck this.", room_id="!room:example.com")

    choose.assert_called_once_with((verse,))
    assert len(maubot_test_bot.responded) == 1
    response = maubot_test_bot.responded[0]
    assert response.room_id == "!room:example.com"
    assert response.content.body == ("> Nebo tak Bůh miloval svět.\n— Jan 3:16 (Bible kralická)")
    assert response.content.get_reply_to() == "test"


@pytest.mark.parametrize("msg_type", [MessageType.TEXT, MessageType.NOTICE, MessageType.EMOTE])
async def test_supported_text_message_types_are_checked(
    maubot_plugin, maubot_test_bot, msg_type: MessageType
) -> None:
    maubot_plugin.verses = (Verse("Žalmy", 1, 1, "Blahoslavený ten muž."),)

    await maubot_test_bot.send("hovno", msg_type=msg_type)

    assert len(maubot_test_bot.responded) == 1


async def test_clean_message_is_ignored(maubot_plugin, maubot_test_bot) -> None:
    await maubot_test_bot.send("Dobrý den všem.")

    assert maubot_test_bot.responded == []


async def test_own_message_is_ignored(maubot_plugin, maubot_test_bot) -> None:
    await maubot_test_bot.send("kurva", sender=maubot_test_bot.client.mxid)

    assert maubot_test_bot.responded == []


async def test_media_message_is_ignored(maubot_plugin, maubot_test_bot) -> None:
    await maubot_test_bot.send("fuck.jpg", msg_type=MessageType.IMAGE)

    assert maubot_test_bot.responded == []
