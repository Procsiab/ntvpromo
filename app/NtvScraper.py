import os
import logging
import traceback
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
    def __init__(self):
        self._set_latest(code='', drop='', period='', before='', number='')
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

    def _scraped_new_latest(self) -> bool:
        try:
            with open(FILE_NAME, 'r') as infile:
                _saved_promo_card = json.load(infile)
                if _saved_promo_card != self._latest:
                    self._write_latest()
                    return True
                else:
                    return False
        except FileNotFoundError:
            self._write_latest()
            return True

    def _write_latest(self):
        global FILE_NAME
        os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
        with open(FILE_NAME, 'w') as outfile:
            outfile.write(json.dumps(self._latest, indent=4, sort_keys=True, default=str))

    def _read_latest(self):
        global FILE_NAME
        try:
            with open(FILE_NAME, 'r') as infile:
                self._latest = json.load(infile)
        except (FileNotFoundError, JSONDecodeError):
            logging.info("Writing new file '{}' with default contents".format(FILE_NAME))
            self._write_latest()

    def _scrape_website(self):
        try:
            if URL.startswith('http'):
                link = urlopen(URL).read()
            else:
                link = open(URL, 'r', encoding='utf-8').read()
        except Exception as e:
            logging.error(f"Failed to fetch URL: {e}")
            self._set_latest(code='N/A', drop='N/A', period='N/A', before='N/A', number='N/A')
            return

        soup = BeautifulSoup(link, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()

        articles = soup.find_all('article')
        for article in articles:
            desc_span = article.find('span', class_=lambda c: c and 'font-400 font-roboto text-text-s' in str(c))
            if not desc_span:
                continue

            desc_text = re.sub(r'\s+', ' ', desc_span.get_text(separator=' ', strip=True))
            if 'codice' not in desc_text.lower() and 'sconto' not in desc_text.lower():
                continue

            avail_text_match = article.find(string=re.compile(r'Posti disponibili', re.IGNORECASE))
            avail_text = re.sub(r'\s+', ' ', avail_text_match.strip()) if avail_text_match else ""

            try:
                # promo code
                code_match = re.search(r'codice\s+(?:con il\s+)?([A-Z0-9]+)', desc_text, re.IGNORECASE)
                str_promo_code = code_match.group(1) if code_match else "N/A"

                # discount
                discounts = re.findall(r'[-]?\d+%', desc_text)
                str_price_drop = ", ".join(discounts) if discounts else "N/A"

                # period
                period_m = re.search(r'dal\s+(\d{1,2}\s+[a-zA-Z]+)\s*(?:al\s+(\d{1,2}\s+[a-zA-Z]+))?', desc_text, re.IGNORECASE)
                if period_m:
                    start_date = period_m.group(1)
                    end_date = period_m.group(2)
                    str_book_period = f"{start_date} - {end_date}" if end_date else start_date
                else:
                    str_book_period = "N/A"

                # deadline
                dl_m = re.search(r'Acquista.*?ore\s+([\d:.]+)\s+del\s+([\d./]+)', desc_text, re.IGNORECASE)
                str_buy_before = f"ore {dl_m.group(1)}, del {dl_m.group(2)}" if dl_m else "N/A"

                # availability
                num_m = re.search(r'Posti disponibili\s*[:\s]*\s*([\d.]+)', avail_text, re.IGNORECASE)
                str_codes_number = num_m.group(1) if num_m else "N/A"

                self._set_latest(
                    code=str_promo_code,
                    drop=str_price_drop,
                    period=str_book_period,
                    before=str_buy_before,
                    number=str_codes_number
                )
                logging.info("Successfully scraped promo code: %s", str_promo_code)
                return

            except Exception as e:
                logging.warning("Error parsing article. Continuing to next.")
                logging.debug(traceback.format_exc())
                continue

        logging.warning("No valid promo codes found on the page.")
        self._set_latest(code='N/A', drop='N/A', period='N/A', before='N/A', number='N/A')

    def get_updates(self) -> dict:
        self._scrape_website()
        if self._scraped_new_latest():
            return self._latest
        else:
            return None
