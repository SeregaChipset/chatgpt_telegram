"""В этом файле определяется классы опенаи для chBot"""
from io import BytesIO
from PIL import Image
import openai
from messages import *


class ChChatGpt:
    def __init__(self, token):
        self.openai = openai
        self.openai.api_key = token
        self.model = "gpt-3.5-turbo"
        self.messages = START_MESSAGE.copy()

    def out(self, quest: str) -> str:
        if len(self.messages) > LEN_MESS:  # если длинна списка запросов больше указанного
            del self.messages[1:3]  # удаляем первый запрос-ответ
        self.messages.append({"role": "user", "content": quest})
        try:
            response = self.openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                temperature=1,
                max_tokens=250,
                top_p=0.9,
            )
            answer = response['choices'][0]['message']['content']
        except Exception as e:
            answer = f"{ERR_MESSAGE} - ({e})"
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    def out_image(self, prompt_image: str) -> str | None:  # запрос к дали
        try:
            response = self.openai.Image.create(
                prompt=prompt_image,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            return image_url  # отдаем поток
        except:
            return None  # обосрался дали

    def out_image_variations(self, img: BytesIO) -> str:
        try:
            # Read the image file from disk and resize it
            image = Image.open(img)
            width, height = 256, 256
            image = image.resize((width, height))

            # Convert the image to a BytesIO object
            byte_stream = BytesIO()
            image.save(byte_stream, format='PNG')
            byte_array = byte_stream.getvalue()

            response = openai.Image.create_variation(
                image=byte_array,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            return image_url  # отдаем поток
        except Exception as e:
            print(e)
            return None  # обосрался дали