#!/usr/bin/env python3

import logging

from pathlib import Path

from NtvPromoBot import NtvPromoBot as BOT

logging.getLogger('httpx').setLevel(logging.WARNING)

TOKEN = ''
AUTH_USER = []


# Look for a secrets folder mounted in the root / (for the Docker container);
# if not present, assume the folder is in the same folder from which the
# command was launched
def _init_secrets():
    global TOKEN
    global AUTH_USER
    _secrets_path = '/auth/'
    _secrets_folder = Path(_secrets_path)
    if not _secrets_folder.exists():
        _secrets_path = './.secrets/'
    with open(_secrets_path + 'TOKEN.secret', 'r') as secret:
        TOKEN = secret.read().rstrip()
    with open(_secrets_path + 'AUTH_USER.secret', 'r') as secret:
        for line in secret:
            AUTH_USER.append(line.rstrip())


# Main routine
def main():
    _init_secrets()
    myBot = BOT(TOKEN, AUTH_USER)
    myBot.run_blocking()


# Run Main
if __name__ == "__main__":
    main()
