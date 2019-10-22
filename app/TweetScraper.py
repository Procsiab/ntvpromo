import json
import logging
import re
from datetime import datetime

from json.decoder import JSONDecodeError
from twitter_scraper import get_tweets

ACCOUNT_NAME = 'ItaloTreno'
TARGET_WORDLIST = ['codice', 'promo', 'risparmi']
FILE_NAME = 'latest.json'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MESSAGE_FORMAT = """🚄 Codice sconto: <b>{string}</b> [{drop}]
⎯⎯⎯⎯⎯⎯⎯⎯
📅 Periodo:\t\t{valid}
⏰ <i>Entro</i>:\t\t{until}
🎫 Disponibilità: {number}
⎯⎯⎯⎯⎯⎯⎯⎯
https://biglietti.italotreno.it"""

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
                    self._latest['text'] = self._format_response(tweet['text'])
                    self._latest['time'] = tweet['time'].strftime(DATE_FORMAT)
                    return True
        return False

    def _check_date(self, timestamp):
        global DATE_FORMAT
        if timestamp > datetime.strptime(self._latest['time'], DATE_FORMAT):
            return True
        else:
            return False

    def _format_response(self, text):
        # Parse the message to find relevant indormation
        _RE_STR = "([A-Z]{3}[A-Z]*)([1-9]0)*"
        _RE_DROP = "([-]*[1-9]{1}[0-9]+%)"
        _RE_NUM = "([1-9]{1}[0-9]*[.][0]{3})"
        _RE_UNTIL = "([Aa]cquista){1}([\D]+)(\d\d)([\D]+)(\d\d\/\d\d)"
        _RE_VALID_START = "([Vv]iagg[io] dal){1}([\D]+)(\d\d)(\s|\/)([a-zA-Z]+|\d\d)"
        _RE_VALID_END = "( al )(\d\d)(\s|\/)([a-zA-z]+|\d\d)"
        code_str = re.search(_RE_STR, text).group()
        code_drop = re.findall(_RE_DROP, text)
        code_num = re.search(_RE_NUM, text)
        if code_num is not None:
            code_num = code_num.group()
        else:
            code_num = "N/A"
        buy_until = re.search(_RE_UNTIL, text).groups()
        buy_until = "{}, ore {}".format(buy_until[4], buy_until[2])
        valid_start = re.search(_RE_VALID_START, text).groups()
        valid_start = valid_start[2] + valid_start[3] + valid_start[4]
        valid_end = re.search(_RE_VALID_END, text)
        if valid_end is not None:
            valid_end = valid_end.groups()
            valid_end = valid_end[1] + valid_end[2] + valid_end[3]
        price_drop = code_drop[0]
        if len(code_drop) == 2:
            price_drop += " - " + code_drop[1]
        code_validity = valid_start
        if valid_end is not None:
            code_validity += " - " + valid_end

        # Build and format the message containing the promo code
        res = MESSAGE_FORMAT.format(string=code_str,
                                    drop=price_drop,
                                    valid=code_validity,
                                    until=buy_until,
                                    number=code_num)
        return res

    def get_updates(self):
        if self._load_tweets():
            self._write_latest()
            return self._latest
        else:
            return None
