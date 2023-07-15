from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных
    db_port: str  # Номер порта


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


class Configs:
    # Инъекции
    _env = Env()
    _tg_bot = TgBot
    _db = DatabaseConfig

    def __init__(self, env_path: str | None = None):
        self._env.read_env(env_path)

        self.tg_bot = self._tg_bot(
            token=self._env('TG_TOKEN'),
            admin_ids=list(map(int, self._env.list('TG_ADMIN_IDS')))
        )
        self.db = self._db(
            database=self._env('DATABASE'),
            db_host=self._env('DB_HOST'),
            db_user=self._env('DB_USER'),
            db_password=self._env('DB_PASSWORD'),
            db_port=self._env('DB_PORT')
        )

    def __str__(self):
        return f'{self.tg_bot}\n{self.db}'
