# bot-saint

A [maubot](https://github.com/maubot/maubot) plugin that replies to Czech or English
profanity with a random verse from the Czech Bible kralická.

The plugin checks text messages, notices, and emotes. Matching is case-insensitive,
ignores Czech diacritics, and only matches whole words. It does not censor or redact the
original message.

## Bible data

The full Bible is bundled in the plugin as `cze-bkr.zefania.xml`, so the plugin makes no
network requests. The text is the public-domain Bible kralická (1613) in Zefania XML
format. It is loaded once when the plugin instance starts and each response is chosen
uniformly from all verses in the file.

## Word list

The Czech and English word list is intentionally small and kept in the source code for
easy review. It was manually curated after evaluating the MIT-licensed
[`washyourmouthoutwithsoap`](https://github.com/thisandagain/washyourmouthoutwithsoap)
lists; its machine-translated Czech false positives and identity slurs were not copied.

## Build and install

The plugin requires maubot 0.6.0 or later.

For development, install [uv](https://docs.astral.sh/uv/) and run:

```sh
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mbc build
```

Upload the resulting `.mbp` file to maubot and create an instance using the desired bot
account. There are no commands, database migrations, or configuration options.

