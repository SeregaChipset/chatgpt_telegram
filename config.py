from dataclasses import dataclass
from environs import Env
import logging

main_logger: logging.Logger = logging.getLogger("Чмоня")
main_logger.setLevel(logging.INFO)
log_handler = logging.FileHandler("log.log", mode='w')
#log_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
log_formatter = logging.Formatter("%(asctime)s %(message)s")
log_handler.setFormatter(log_formatter)
main_logger.addHandler(log_handler)

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
    logger: logging.Logger


def load_config() -> Config:
    return Config(token_openai=env('OPENAI_API_KEY'), token_tg=env('TOKEN_TG'),
                  image_size=IMAGE_SIZE, image_resize=IMAGE_RESIZE, proxy=env('PROXY'),
                  logger=main_logger)
