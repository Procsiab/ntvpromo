#!/usr/bin/env python3

from NtvPromoBot import NtvPromoBot as BOT
from pathlib import Path

TOKEN = ''
AUTH_USER = ''


def _init_secrets():
    global TOKEN
    global AUTH_USER
    _secrets_path = '/secrets/'
    _secrets_folder = Path(_secrets_path)
    if not _secrets_folder.exists():
        _secrets_path = './.secrets/'
    with open(_secrets_path + 'TOKEN.secret', 'r') as secret:
        TOKEN = secret.read().rstrip()
    with open(_secrets_path + 'AUTH_USER.secret', 'r') as secret:
        AUTH_USER = secret.read().rstrip()


# Main routine
def main():
    _init_secrets()
    myBot = BOT(TOKEN, AUTH_USER)
    try:
        myBot.run()
    finally:
        myBot.halt()


# Run Main
if __name__ == "__main__":
    main()
