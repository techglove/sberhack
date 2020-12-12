import os

from dotenv import load_dotenv


load_dotenv(dotenv_path=f'{os.path.dirname(os.path.abspath(__file__))}/.env.prod')

DB_LOGIN = os.getenv("LOGIN")
DB_PASSWORD = os.getenv("PASSWORD")
DB_DATABASE = os.getenv("DATABASE")
DB_HOST = os.getenv("HOST")
