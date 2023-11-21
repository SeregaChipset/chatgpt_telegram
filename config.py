from dataclasses import dataclass
from environs import Env

env: Env = Env()
env.read_env()

#настройки опенаи
#разрешение картинки на выход
IMAGE_SIZE = "256x256"
#разрешение картинки сжимайемой на вход
IMAGE_RESIZE = 256, 256

@dataclass
class Config:
    token_openai: str
    token_tg: str
    proxy: str
    image_size: str
    image_resize: tuple


def load_config() -> Config:
    return Config(token_openai=env('OPENAI_API_KEY'), token_tg=env('TOKEN_TG'),
                  image_size=IMAGE_SIZE, image_resize=IMAGE_RESIZE, proxy=env('PROXY'))
