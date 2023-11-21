# SeregaChipset bot v02
import config
from bot_class import ChBot
from config import *


if __name__ == '__main__':  # луп
    bot = ChBot(config.load_config())
    bot.start_polling()
