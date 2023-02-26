import logging

from telegram import ParseMode
from telegram.ext import CallbackContext, CommandHandler, Updater
from telegram.error import Unauthorized, TimedOut, NetworkError
from NtvScraper import NtvScraper as SCRAPER

logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=logging.INFO)

UPDATE_INTERVAL = 600
MESSAGE_FORMAT = """🚄 Codice sconto: <b>{code}</b> [{drop}]
⎯⎯⎯⎯⎯⎯⎯⎯
📅 Periodo:\t\t{period}
⏰ <i>Entro</i>:\t\t{before}
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
        self._job_queue.run_repeating(self._callback_scraper,
                                      interval=UPDATE_INTERVAL, first=1)

    def _callback_start(self, update, context):
        logging.info("The user {} [{}] has called the start function"
                     .format(update.message.from_user['username'],
                             update.message.chat_id))
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="This bot will only talk to authorized users!")

    def _callback_scraper(self, context: CallbackContext):
        promo_card = self._scraper.get_updates()
        if promo_card is not None:
            for user in self._auth_user:
                try:
                    context.bot.send_message(chat_id=user,
                                             text=self._format_response(promo_card),
                                             parse_mode=ParseMode.HTML)
                    logging.info("Sent update to the user {}".format(user))
                except Unauthorized:
                    logging.warn("The user {} has blocked this bot".format(user))
                except (TimedOut, NetworkError):
                    logging.warn("A network error occurred during the message sending")
        else:
            logging.info("No recent promo codes from @ItaloTreno")

    def _format_response(self, promo_card: dict):
        # Build and format the message containing the promo code
        text = MESSAGE_FORMAT.format(code=promo_card["code"],
                                     drop=promo_card["drop"],
                                     period=promo_card["period"],
                                     before=promo_card["before"],
                                     number=promo_card["number"])
        return text

    def run(self):
        self._updater.start_polling()
        logging.info("Bot started, press CTRL+C to stop it")
        self._updater.idle()

    def halt(self):
        logging.info("Tearing down the Bot service")
        self._updater.stop()
