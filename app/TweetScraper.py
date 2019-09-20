from twitter_scraper import get_tweets
from datetime import datetime

ACCOUNT_NAME = 'ItaloTreno'
TARGET_WORDLIST = ['codice', 'promo', 'risparmi']


class TweetScraper:

    def __init__(self):
        self._latest = {'text': "", 'time': datetime(2000, 1, 1)}

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
        if timestamp > self._latest['time']:
            return True
        else:
            return False

    def get_updates(self):
        if self._load_tweets():
            return self._latest
        else:
            return None

    def get_latest(self):
        return self._latest
