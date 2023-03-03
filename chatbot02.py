#SeregaChipset bot v02
from bot_class import ChBot
from config import *

if __name__ == '__main__': #луп
    bot = ChBot(TOKEN_TG, API_AI)
    bot.start_polling()