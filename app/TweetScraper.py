import json
import logging
from datetime import datetime

from json.decoder import JSONDecodeError
from twitter_scraper import get_tweets

ACCOUNT_NAME = 'ItaloTreno'
TARGET_WORDLIST = ['codice', 'promo', 'risparmi']
FILE_NAME = 'latest.json'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=logging.INFO)


class TweetScraper:

    # Initialize the _latest tweet attribute and try to read it from file
    def __init__(self):
        global DATE_FORMAT
        self._latest = {'text': "",
                        'time': datetime(2000, 1, 1).strftime(DATE_FORMAT)}
        self._read_latest()

    # Write to file the _latest attribute, as JSON
    def _write_latest(self):
        global FILE_NAME
        with open(FILE_NAME, 'w') as outfile:
            outfile.write(json.dumps(self._latest, indent=4,
                                     sort_keys=True, default=str))

    # Try to read the _latest attribute from file, and create the file
    # if not present
    def _read_latest(self):
        global FILE_NAME
        try:
            with open(FILE_NAME, 'r') as infile:
                self._latest = json.load(infile)
        except (FileNotFoundError, JSONDecodeError):
            logging.info("Writing a new file with default contents"
                         .format(FILE_NAME))
            self._write_latest()

    def _load_tweets(self):
        global ACCOUNT_NAME
        recent_tweets = get_tweets(ACCOUNT_NAME, pages=1)
        return self._get_latest(recent_tweets)

    def _get_latest(self, tweet_list):
        global TARGET_WORDLIST
        for tweet in tweet_list:
            if any(word in tweet['text'] for word in TARGET_WORDLIST):
                if self._check_date(tweet['time']):
                    self._latest['text'] = tweet['text']
                    self._latest['time'] = tweet['time']
                    return True
        return False

    def _check_date(self, timestamp):
        global DATE_FORMAT
        if timestamp > datetime.strptime(self._latest['time'], DATE_FORMAT):
            return True
        else:
            return False

    def get_updates(self):
        if self._load_tweets():
            self._write_latest()
            return self._latest
        else:
            return None

    def get_latest(self):
        return self._latest
