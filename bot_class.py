"""В этом файле определяется класс chBot"""
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import aiogram.utils
from openai_class import ChChatGpt
from messages import *


class ChBot:
    def __init__(self, token_tg, api_ai):
        self.bot = Bot(token=token_tg)
        self.dp = Dispatcher(self.bot)
        self.ch_openai = ChChatGpt(api_ai)

        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.register_message_handler(self.help, commands=['help'])
        self.dp.register_message_handler(self.debug, commands=['debug'])
        self.dp.register_message_handler(self.message)

        # добавляем кнопки
        help_button = types.KeyboardButton('/help')
        empty_button = types.KeyboardButton('/debug')
        self.custom_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row(help_button, empty_button)

    def del_name(self, stroka, temp_list): #функция удаления обращения чмоня
        i = temp_list.index(NAME.lower())
        if i > 2: #логика такова, что удалению подлежит только чмоня в первых 3 позициях
            return stroka
        temp_list = stroka.split()
        del temp_list[i]
        return ' '.join(temp_list)

    async def start(self, message: types.Message): #старт меню
        await message.reply(HELLO_MESSAGE, reply_markup=self.custom_keyboard)

    async def help(self, message: types.Message): #хелп меню
        await message.reply(HELP_MESSAGE)
        with open('help.png', 'rb') as photo:
            await self.bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(photo))

    async def debug(self, message: types.Message): #получить ид чата + список сообщений
        await message.reply(message.chat.id)
        await self.bot.send_message(message.chat.id, self.ch_openai.messages)

    async def message(self, message: types.Message): # функция обмена сообщениями
        msg_list = [slovo.strip('!.,%:\'\"\\/*;?') for slovo in message.text.lower().split()] #создает список слов

        if NAME.lower() in msg_list: #если зовут по имени
            text = self.ch_openai.out(self.del_name(message.text, msg_list))  #запрашивает ответ у чатгпт
            print(self.del_name(message.text, msg_list), text) #отладка
            await self.bot.send_message(message.chat.id, text) #отвечает

        if 'картинка' in msg_list: #реагирует на слово картинки
            input_io = self.ch_openai.out_image(message.text.replace('картинка', '')) # запрос
            if input_io:
                photo = types.InputFile(input_io, filename='image.png') #возвращаем картинку в нужном для аиограм виде
                await self.bot.send_photo(chat_id=message.chat.id, photo=photo)
            else:
                await self.bot.send_message(message.chat.id, 'Дали походу наебнулась')

    def start_polling(self):
        aiogram.executor.start_polling(self.dp)