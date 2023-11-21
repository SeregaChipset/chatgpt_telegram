"""В этом файле определяется классы опенаи для chBot"""
from io import BytesIO
from PIL import Image
from openai import AsyncOpenAI
from messages import *
import httpx


class ChChatGpt:
    def __init__(self, token: str, model: str, img_size="256x256", img_resize=(256, 256), max_tokens: int=500,
                 proxy: str = None):
        self.openai = AsyncOpenAI(api_key=token, http_client=httpx.AsyncClient(
            proxies=proxy))
        self.model = model
        self.messages = START_MESSAGE.copy()
        self.IMAGE_SIZE = img_size
        self.IMAGE_RESIZE = img_resize
        self.max_tokens = max_tokens

    async def out(self, quest: str) -> str:
        if len(self.messages) > LEN_MESS:  # если длинна списка запросов больше указанного
            del self.messages[1:3]  # удаляем первый запрос-ответ
        self.messages.append({"role": "user", "content": quest})
        try:
            response = await self.openai.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=1,
                max_tokens=self.max_tokens,
                top_p=0.9,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"{ERR_MESSAGE} - ({e})"
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    async def out_image(self, prompt_image: str) -> str | None:  # запрос к дали
        try:
            response = await self.openai.images.generate(
                prompt=prompt_image,
                n=1,
                size=self.IMAGE_SIZE
            )
            image_url = response.data[0].url
            return image_url  # отдаем поток
        except:
            return None  # обосрался дали

    async def out_image_variations(self, img: BytesIO) -> str:
        try:
            # Читает поток изменяя его размер
            image = Image.open(img)
            width, height = self.IMAGE_RESIZE
            image = image.resize((width, height))

            # Convert the image to a BytesIO object
            byte_stream = BytesIO()
            image.save(byte_stream, format='PNG')
            byte_array = byte_stream.getvalue()

            response = await self.openai.images.create_variation(
                image=byte_array,
                n=1,
                size=self.IMAGE_SIZE
            )
            image_url = response.data[0].url
            return image_url  # отдаем поток
        except Exception as e:
            print(e)
            return None  # обосрался дали