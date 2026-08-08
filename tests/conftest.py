from __future__ import annotations

import pytest
import pytest_asyncio
from maubot.testing import TestBot

from sadparad1se_bot_saint import SaintBot

pytest_plugins = ["maubot.testing.fixtures"]


@pytest_asyncio.fixture
async def maubot_test_bot():
    bot = TestBot()
    yield bot
    await bot.client.api.session.close()


@pytest.fixture
def maubot_plugin_class():
    return SaintBot


@pytest.fixture
def maubot_plugin_config():
    return None


@pytest.fixture
def maubot_plugin_db():
    # maubot 0.6.0's default async fixture exits before yielding when database=false.
    return None
