# NTV Promo Code bot

#### Description

This repository contains the code for a docker-compose deployable Telegram bot, which uses the [Telegram Python API](https://github.com/python-telegram-bot/python-telegram-bot) and this [Twitter Javascript API scraper](https://github.com/bisguzar/twitter-scraper); the bot itself will just look for the latest promo code related tweet among the ones on the first page of the **ItaloTreno** account, by scraping it every ten minutes.

Also, the Docker Images for ARMv7, AARCH64 and x86\_X64 platforms are automatically built from this repository, and available from [Docker Hub](https://hub.docker.com/r/procsiab/ntvpromo)

## Building with Dockerfile

The Dockerfile is written to allow cross-architecture builds, using QEMU's user-static package: to build the image on x86 for another platform do the following:

- be sure to install `qemu-user-static` if you need to run the container on an architecture different from the local one;
- to build the container for *aarch64*, run `cp $(which qemu-aarch64-static) .`;
- run the build process with `docker build -t myregistry/ntvpromo:arm64 .`.

If you want to use a target architecture different from ARM 64 bit, just change the Dockerfile according to the needed _qemu-static-*_ binary file, and copy it into the repo directory as shown above. Also, remember to specify the correct base image at the beginning of the Dockerfile.

## Installing secrets

The Python code assumes the existence of the folder `.secret` in the repository's root directory; inside it, two file should be placed, as in the following structure example:

```
.secrets
├── AUTH_USER.secret
└── TOKEN.secret
```

The `.secret` text files should contain the following data:
- AUTH\_USER: a Telegram user ID or a group ID to post the updates into;
- TOKEN: a Telegram bot token, which can be obtained from BotFather.

*NOTE*: the code provided in this repository will not work without such secret files!

## Running with Docker Compose

You may first choose the correct image for the host CPU architecture; change the `image:` property using either the `amd64`, `arm64` or the `arm32` tag. The default is `amd64`.

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
cd app
python3 main.py
```

The bot should start logging some info.
