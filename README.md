# NTV Promo Code bot

[![Container Build](https://github.com/Procsiab/ntvpromo/actions/workflows/build-container-publish-dockerhub.yaml/badge.svg)](https://github.com/Procsiab/ntvpromo/actions/workflows/build-container-publish-dockerhub.yaml)

![Docker Image Version (latest by date)](https://img.shields.io/docker/v/procsiab/ntvpromo?label=Latest%20tag%20pushed%20on%20Docker%20Hub)

#### Description

This repository contains the code for a container-compose deployable Telegram bot, which uses the [Telegram Python API](https://github.com/python-telegram-bot/python-telegram-bot) and [BeautifulSoup scraper](https://beautiful-soup-4.readthedocs.io/en/latest/); the bot itself will extract some keywords from the offer page on ItaloTreno's website, by scraping it every ten minutes and sending an update if that strings differs from the ones previously saved.

Also, the Container Images for ARMv7, AARCH64 and x86\_64 platforms are automatically built from this repository, and available from [Docker Hub](https://hub.docker.com/r/procsiab/ntvpromo)

## Building with Containerfile

The Containerfile is written to allow cross-architecture builds, using QEMU's user-static package: to build the image on x86 for another platform do the following:

- be sure to install `qemu-user-static` if you need to run the container on an architecture different from the local one;
- to build the container for *aarch64*, run `cp $(which qemu-aarch64-static) .`;
- run the build process with `podman build -t myregistry/ntvpromo:latest -f Containerfile.aarch64 .`.

If you want to use a target architecture different from ARM 64 bit, just change the Containerfile according to the needed _qemu-static-*_ binary file, and copy it into the repo directory as shown above. Also, remember to specify the correct base image at the beginning of the Containerfile.

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

## Running with Podman Compose

You may first choose the correct image for the host CPU architecture; change the `image:` property using either the `amd64`, `aarch64` or the `armv7` tag. The default is `amd64`.

Open the repository's root directory in a terminal and issue the following command:

```bash
podman-compose up -d
```

## Running on the host with venv

Open the repository's root directory in a terminal and issue the following command:
```bash
python3 -m venv app/.venv
source app/.venv/bin/activate
pip3 install -U pip
pip3 install -U -r app/requirements.txt
export TZ="Europe/Rome"
mkdir data
python3 app/main.py
```

The bot should start logging some info.

### Change the log verbosity

You may run the script with a different verbosity, for example to run it at the DEBUG level, export the `LOGLEVEL` variable with the desired value:

```bash
LOGLEVEL='DEBUG' python3 app/main.py
```
