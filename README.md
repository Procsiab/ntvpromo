# NTV Promo Code bot

#### Description:

This repository contains the code for a docker-compose deployable Telegram bot, which uses the [Telegram Python API](https://github.com/python-telegram-bot/python-telegram-bot) and this [Twitter Javascript API scraper](https://github.com/bisguzar/twitter-scraper); the bot itself will just look for the latest promo code related tweet among the ones on the first page of the **ItaloTreno** account, by scraping it every ten minutes.

## Installing secrets

The Python code assumes the existence of the folder `.secret` in the repository's root directory; inside it, two file should be placed, as in the following structure example:

```
.secrets
├── AUTH_USER.secret
└── TOKEN.secret
```

The `.secret` text files should contain the following data:
- AUTH_USER: a Telegram user ID or a group ID to post the updates into;
- TOKEN: a Telegram bot token, which can be obtained from BotFather.

*NOTE*: the code provided in this repository will not work without such secret files!

## Running with Docker Compose

Open the repository's root directory in a terminal and issue the following command:

```bash
docker-compose up -d
```

## Running on the host with venv

Open the repository's root directory in a terminal and issue the following command:
```bash
python3 -m venv app/.venv
source app/.venv/bin/activate
pip3 install -U pip
pip3 install -U -r app/requirements.txt
python3 app/main.py
```

The bot should start logging some info.
