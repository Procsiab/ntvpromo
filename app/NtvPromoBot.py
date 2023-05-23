import os
import logging

from telegram import ForceReply
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CommandHandler, JobQueue, Updater
from telegram.error import Forbidden, TimedOut, NetworkError
from NtvScraper import NtvScraper as SCRAPER

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=LOGLEVEL)

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
        self._job_queue = JobQueue()
        self._app = Application.builder().token(telegram_token).job_queue(self._job_queue).build()
        self._auth_user = auth_user
        self._updater = Updater(self._app.bot, self._job_queue)
        # Add handlers and jobs to the dispatcher
        self._app.add_handler(CommandHandler("start", self._command_start))
        self._job_queue.run_repeating(self._callback_scraper,
                                      interval=UPDATE_INTERVAL, first=1)

    async def _command_start(self, update, context):
        logging.info("The user {} [{}] has called the start function"
                     .format(update.message.from_user['username'],
                             update.message.chat['id']))
        await update.message.reply_html(
            "This bot will only talk to authorized users!",
            reply_markup=ForceReply(selective=True),
        )

    async def _callback_scraper(self, context: CallbackContext):
        promo_card = self._scraper.get_updates()
        if promo_card is not None:
            for user in self._auth_user:
                try:
                    await context.bot.send_message(chat_id=user,
                                                   text=self._format_response(promo_card),
                                                   parse_mode=ParseMode.HTML)
                    logging.info("Sent update to the user {}".format(user))
                except Forbidden:
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

    def run_blocking(self):
        self._app.run_polling()
