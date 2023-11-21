"""В этом файле определяется класс chBot
aiogram версии 3
"""
from aiogram import Bot, F, types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from openai_class import ChChatGpt
from messages import *
from io import BytesIO


class ChBot:
    def __init__(self, config):
        self.bot: Bot = Bot(token=config.token_tg)
        self.dp: Dispatcher = Dispatcher()
        self.api_ai: str = config.token_openai
        self.chats: dict = {}  # будущий список чатов
        self.IMAGE_SIZE = config.image_size
        self.IMAGE_RESIZE = config.image_resize
        self.proxy = config.proxy

        # регистрирую хендлеры
        self.dp.message.register(self.start, Command(commands=["start"]))
        self.dp.message.register(self.debug, Command(commands=["debug"]))
        self.dp.message.register(self.god_mode, Command(commands=["god_mode"]))
        self.dp.message.register(self.help, F.text.startswith("help"))
        self.dp.message.register(self.variation, F.photo)
        self.dp.message.register(self.message)

        # добавляем кнопки
        # Создаем кнопки с хелпом и картинкой
        button_help: KeyboardButton = KeyboardButton(text="help")
        button_image: KeyboardButton = KeyboardButton(text="картинка красивая картинка")
        
        # Создаем клавиатуру
        self.kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                            keyboard=[[button_help],
                                                      [button_image],
                                                      ],
                                            one_time_keyboard=True,
                                            resize_keyboard=True)

    def check_chat_id(self, chatid: int) -> bool:
        # функция проверки присутствия чата с пользователем
        # вернет False и создаст в словаре отдельный обьект опенаи, если чата не было, иначе True
        if chatid not in self.chats:
            self.chats[chatid] = ChChatGpt(token=self.api_ai, model='gpt-3.5-turbo',
                                           img_size=self.IMAGE_SIZE, img_resize=self.IMAGE_RESIZE, proxy=self.proxy)
            return False
        return True

    @staticmethod
    def del_name(stroka: str, temp_list: list[str]) -> str:
        # функция удаления обращения чмоня
        i = temp_list.index(NAME.lower())
        if i > 2:  # логика такова, что удалению подлежит только чмоня в первых 3 позициях
            return stroka
        temp_list = stroka.split()
        del temp_list[i]
        return ' '.join(temp_list)

    async def god_mode(self, message: types.Message):
        # дает пользователю чат с большим числом токенов и гпт4
        chatid: int = message.chat.id
        if chatid in self.chats:
            del self.chats[chatid]
        self.chats[chatid] = ChChatGpt(token=self.api_ai, model='gpt-4-1106-preview',
                                       img_size=self.IMAGE_SIZE, img_resize=self.IMAGE_RESIZE, max_tokens=1000,
                                       proxy=self.proxy)
        await message.reply('Теперь ответы пишет GPT4, максимальный размер ответа увеличен.')

    async def start(self, message: types.Message):
        # старт меню
        chat_id = message.chat.id
        self.check_chat_id(chat_id)
        await message.reply(HELLO_MESSAGE, reply_markup=self.kb)

    async def help(self, message: types.Message):
        # хелп меню
        await message.reply(HELP_MESSAGE)
        await self.bot.send_photo(chat_id=message.chat.id, photo=types.FSInputFile("help.png"))

    async def debug(self, message: types.Message):
        # получить ид чата + список сообщений
        chat_id = message.chat.id
        await message.reply(str(message.chat.id))
        if self.chats:
            await self.bot.send_message(message.chat.id, str(self.chats[chat_id].messages))

    async def variation(self, message: types.Message):
        # функция возврата вариации изображения, фильтр по картинкам
        chat_id = message.chat.id
        self.check_chat_id(chat_id)
        photo_file = await self.bot.get_file(message.photo[-1].file_id)  # получение ид файла картинки
        # скачиваем картинку и запихиваем ее в поток байт
        image_input: BytesIO = await self.bot.download_file(photo_file.file_path)

        image_output: str = await self.chats[chat_id].out_image_variations(image_input)  # запрос
        if image_output:
            await self.bot.send_photo(chat_id=message.chat.id, photo=image_output)
        else:
            await self.bot.send_message(message.chat.id, 'Дали походу наебнулась')

    async def message(self, message: types.Message):
        # функция обмена сообщениями
        chat_id = message.chat.id
        self.check_chat_id(chat_id)
        msg_list = [slovo.strip('!.,%:\'\"\\/*;?') for slovo in message.text.lower().split()]  # создает список слов

        if message.chat.type == "private":  # личная беседа
            text = await self.chats[chat_id].out(message.text)  # запрашивает ответ у чатгпт
            print(message.text, text)  # отладка
            await self.bot.send_message(message.chat.id, text)  # отвечает
        elif NAME.lower() in msg_list:  # если зовут по имени (для групп)
            text = self.chats[chat_id].out(self.del_name(message.text, msg_list))  # запрашивает ответ у чатгпт
            print(self.del_name(message.text, msg_list), text)  # отладка
            await self.bot.send_message(message.chat.id, text)  # отвечает

        if 'картинка' in msg_list:  # реагирует на слово картинки
            image_input: str = await self.chats[chat_id].out_image(message.text.replace('картинка', ''))  # запрос
            if image_input:
                await self.bot.send_photo(chat_id=message.chat.id, photo=image_input)
            else:
                await self.bot.send_message(message.chat.id, 'Дали походу наебнулась')

    def start_polling(self):
        self.dp.run_polling(self.bot)
        