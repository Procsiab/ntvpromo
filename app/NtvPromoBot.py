import logging
import re
from re import *

from telegram import ParseMode
from telegram.ext import CallbackContext, CommandHandler, Updater
from TweetScraper import TweetScraper as SCRAPER

logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=logging.INFO)

UPDATE_INTERVAL = 600
MESSAGE_FORMAT = """🚄 Codice sconto: <b>{string}</b> [{drop}]
⎯⎯⎯⎯⎯⎯⎯⎯
📅 Periodo:\t\t{valid}
⏰ <i>Entro</i>:\t\t{until}
🎫 Disponibilità: {number}
⎯⎯⎯⎯⎯⎯⎯⎯
https://biglietti.italotreno.it"""


class NtvPromoBot:

    def __init__(self, telegram_token, auth_user):
        self._scraper = SCRAPER()
        self._updater = Updater(token=telegram_token, use_context=True)
        self._auth_user = auth_user
        self._dispatcher = self._updater.dispatcher
        self._job_queue = self._updater.job_queue
        # Add handlers and jobs to the dispatcher
        start_handler = CommandHandler('start', self._callback_start)
        self._dispatcher.add_handler(start_handler)
        self._job_queue.run_repeating(self._callback_twitter,
                                      interval=UPDATE_INTERVAL, first=1)

    def _callback_start(self, update, context):
        logging.info("The user {} [{}] has called the start function"
                     .format(update.message.from_user['username'],
                             update.message.chat_id))
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="This bot will only talk to authorized users!")

    def _callback_twitter(self, context: CallbackContext):
        response = self._scraper.get_updates()
        if response is not None:
            for user in self._auth_user:
                context.bot.send_message(chat_id=user,
                                         text=self._format_response(response['text']),
                                         parse_mode=ParseMode.HTML)
                logging.info("Sent update to the user {}".format(user))
        else:
            logging.info("No recent promo codes from @ItaloTreno")

    def _format_response(self, text):
        # Parse the message to find relevant indormation
        _RE_STR = "([A-Z]{3}[A-Z]*)([1-9]0)*"
        _RE_DROP = "([-]*[1-9]{1}[0-9]+%)"
        _RE_NUM = "([1-9]{1}[0-9]*[.][0]{3})"
        _RE_UNTIL = "([Aa]cquista){1}([\D]+)(\d\d)([\D]+)(\d\d\/\d\d)"
        _RE_VALID_START = "([Vv]iagg[io] dal){1}([\D]+)(\d\d|\d)(\s|\/)([a-zA-Z]+|\d\d|\d)"
        _RE_VALID_END = "( al )(\d\d|\d)(\s|\/)([a-zA-z]+|\d\d|\d)"
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
        if len(code_drop) > 1:
            price_drop += ", " + code_drop[1]
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

    def run(self):
        self._updater.start_polling()
        logging.info("Bot started, press CTRL+C to stop it")
        self._updater.idle()

    def halt(self):
        logging.info("Tearing down the Bot service")
        self._updater.stop()
