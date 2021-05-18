import json
import logging
from datetime import datetime

from json.decoder import JSONDecodeError
from os import environ
import pytz
import twint

ACCOUNT_NAME = 'ItaloTreno'
TWEET_BUF_SIZE = 20
TARGET_WORDLIST = ['codice', 'promo', 'risparmi']
FILE_NAME = 'data/latest.json'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=logging.INFO)


class TweetScraper:

    # Initialize the _latest tweet attribute and try to read it from file
    def __init__(self):
        global DATE_FORMAT
        global ACCOUNT_NAME
        global TWEET_BUF_SIZE
        self._timezone = pytz.timezone(environ["TZ"])
        # Scraping settings
        self._twint_config = twint.Config()
        self._twint_config.Username = ACCOUNT_NAME
        self._twint_config.Store_object = True
        self._twint_config.Hide_output = True
        sample_time = self._timezone.localize(datetime(2000, 1, 1))
        self._latest = {'text': "",
                        'time': sample_time.strftime(DATE_FORMAT)}
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
            logging.info("Writing new file '{}' with default contents"
                         .format(FILE_NAME))
            self._write_latest()
        finally:
            date_without_time = self._latest["time"].split(' ')[0]
            self._twint_config.Since = date_without_time

    def _load_tweets(self):
        self._read_latest()
        twint.run.Search(self._twint_config)
        recent_tweets = twint.output.tweets_list
        return self._get_latest(recent_tweets)

    def _get_latest(self, tweet_list):
        global TARGET_WORDLIST
        for tweet in tweet_list:
            if any(word in tweet.tweet for word in TARGET_WORDLIST):
                # Pass a timezone-naive datetime to the check_date method
                if self._check_date(tweet.datetime):
                    self._latest['text'] = tweet.tweet
                    self._latest['time'] = tweet.datetime
                    return True
        return False

    def _check_date(self, timestamp):
        global DATE_FORMAT
        if datetime.strptime(timestamp, DATE_FORMAT) > datetime.strptime(self._latest['time'], DATE_FORMAT):
            return True
        else:
            return False

    def get_updates(self):
        if self._load_tweets():
            self._write_latest()
            self._read_latest()
            return self._latest
        else:
            return None
