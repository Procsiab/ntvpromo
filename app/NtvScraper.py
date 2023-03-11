import os
import logging
import traceback
import sys

import json
from json.decoder import JSONDecodeError
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=LOGLEVEL)

URL = 'https://www.italotreno.it/it/offerte-treno/codicepromo'
FILE_NAME = 'data/latest.json'


class NtvScraper:

    # Initialize the _latest tweet attribute and try to read it from file
    def __init__(self):
        # Scraping settings
        self._set_latest(code='',
                         drop='',
                         period='',
                         before='',
                         number='')
        self._read_latest()

    def _set_latest(self, code: str, drop: str, period: str, before: str, number: str):
        self._latest = {
            'code': code,
            'drop': drop,
            'period': period,
            'before': before,
            'number': number
        }
        logging.debug("NtvScraper: Updated self._latest {}".format(json.dumps(self._latest)))

    # Return True if the saved latest differs from the _latest attribute
    # and write it to file
    def _scraped_new_latest(self) -> bool:
        with open(FILE_NAME, 'r') as infile:
            _saved_promo_card = json.load(infile)
            if _saved_promo_card != self._latest:
                self._write_latest()
                return True
            else:
                return False

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

    def _scrape_website(self):
        # Allow for both remote and local HTML parsing
        if URL.startswith('http'):
            link = urlopen(URL).read()
        else:
            link = open(URL)
        # Create the Soup and remove any style or script
        soup = BeautifulSoup(link, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        # Traverse the promo table and locate only the offer codes
        promo_table = soup.find_all(class_="content content-single--default grid-container cards-1col --new")
        for promo_card in promo_table:
            isPromoCode = True if promo_card.find("h3", string=re.compile('Codic[ei] Promo|PROMO.*')) else False
            if isPromoCode:
                promo_desc = promo_card.find(class_="content__subtitle")
                promo_avail = promo_card.find(class_="content__testo")
                _RE_CODE = r"<strong>([A-Z]{3}[A-Z]*)([0-9]+)?<\/strong>"
                _RE_DROP = r"([-]*[1-9]{1}[0-9]+%)"
                _RE_BOOK_START = r" dal(l')?( )?[\D]+(\d\d|\d)(\s|\/|\.)([a-zA-Z]+|\d\d|\d)"
                _RE_BOOK_END = r" al [\D]+(\d\d|\d)(\s|\/|\.)([a-zA-Z]+|\d\d|\d)"
                _RE_BUY_BEFORE = r"([Aa]cquista){1}[\D]+(\d\d)(.00)?[\D]+(\d+\/\d+|\d+\.\d+)"
                _RE_CODES_NUM = r"([1-9]{1}[0-9]*[.]?[0]{3})"
                try:
                    # Extract code
                    str_promo_code = re.search(_RE_CODE, str(promo_desc)).groups()
                    str_promo_code = ''.join(item for item in str_promo_code if item)
                    logging.debug("Parsed code: {}".format(str_promo_code))
                    # Extract discount
                    str_price_drop = re.findall(_RE_DROP, str(promo_desc))
                    str_price_drop = str_price_drop[0] + ", " + str_price_drop[1] if len(str_price_drop) > 1 else str_price_drop[0]
                    logging.debug("Parsed discount: {}".format(str_price_drop))
                    # Extract booking period
                    str_book_start = re.search(_RE_BOOK_START, str(promo_desc)).groups()
                    str_book_start = ''.join(item for item in str_book_start[1:] if item)
                    str_book_end = re.search(_RE_BOOK_END, str(promo_desc))
                    str_book_period = str_book_start
                    if str_book_end is not None:
                        str_book_end = ''.join(item for item in str_book_end.groups() if item)
                        str_book_period += " - " + str_book_end
                    logging.debug("Parsed booking period: {}".format(str_book_period))
                    # Extract promo deadline
                    str_buy_before = re.search(_RE_BUY_BEFORE, str(promo_avail)).groups()
                    str_buy_before = "{}, ore {}".format(str_buy_before[3], str_buy_before[1])
                    logging.debug("Parsed promo deadline: {}".format(str_buy_before))
                    # Extract codes number
                    str_codes_number = re.search(_RE_CODES_NUM, str(promo_avail))
                    str_codes_number = str_codes_number.group() if str_codes_number is not None else "N/A"
                    logging.debug("Parsed codes number {}".format(str_codes_number))
                    # Save parsed info to class attribute
                    self._set_latest(code=str_promo_code,
                                     drop=str_price_drop,
                                     period=str_book_period,
                                     before=str_buy_before,
                                     number=str_codes_number)
                    break
                except AttributeError:
                    print("Error occurred while parsing promo code!")
                    traceback.print_exception(*sys.exc_info())

    def get_updates(self) -> dict:
        self._scrape_website()
        if self._scraped_new_latest():
            return self._latest
        else:
            return None
