from dataclasses import dataclass
from environs import Env
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass
class TgBot:
    token: str
    admin_ids: list[str]

@dataclass
class Config:
    tg_bot: TgBot

def load_config(path: str | None = None) -> None:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), admin_ids=env.list('ADMIN_IDS')))


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file='', env_file_encoding='utf-8')


settings = Settings()
