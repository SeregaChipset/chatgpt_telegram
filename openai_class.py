"""В этом файле определяется классы опенаи для chBot"""
import os
import io
import requests
import openai
from messages import *


class ChChatGpt:
    def __init__(self, token):
        self.openai = openai
        self.openai.api_key = token
        self.model = "gpt-3.5-turbo"
        self.messages = START_MESSAGE

    def out(self, quest):
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

    def out_image(self, prompt_image):  # запрос к дали
        try:
            response = self.openai.Image.create(
                prompt=prompt_image,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            return io.BytesIO(requests.get(image_url).content)  # отдаем поток
        except:
            return None  # обосрался дали
