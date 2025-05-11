from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    # Создаем экземпляр класса Env
    env: Env = Env()

    # Добавляем в переменные окружения данные, прочитанные из файла .env
    env.read_env(path)

    # Создаем экземпляр класса Config и наполняем его данными из переменных окружения
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        ),
        db=DatabaseConfig(
            database=env('DATABASE'),
            db_host=env('DB_HOST') or None,
            db_user=env('DB_USER') or None,
            db_password=env('DB_PASSWORD') or None
        )
    )
