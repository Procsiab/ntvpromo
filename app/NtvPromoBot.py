import logging

from telegram.ext import CallbackContext, CommandHandler, Updater
from TweetScraper import TweetScraper as SCRAPER

logging.basicConfig(format='\n[%(asctime)s]: %(name)s (%(levelname)s)\n - %(message)s',
                    level=logging.INFO)

UPDATE_INTERVAL = 600


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
                                      interval=UPDATE_INTERVAL, first=0)

    def _callback_start(self, update, context):
        logging.info("The user {} [{}] has called the start function"
                     .format(update.message.from_user['username'],
                             update.message.chat_id))
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="This bot will only talk to authorized users!")

    def _callback_twitter(self, context: CallbackContext):
        response = self._scraper.get_updates()
        if response is not None:
            context.bot.send_message(chat_id=self._auth_user,
                                     text=response['text'])
            logging.info("Sent update to the user {}".format(self._auth_user))
        else:
            logging.info("No recent promo codes from @ItaloTreno")

    def run(self):
        self._updater.start_polling()
        logging.info("Bot started, press CTRL+C to stop it")
        self._updater.idle()

    def halt(self):
        logging.info("Tearing down the Bot service")
        self._updater.stop()
