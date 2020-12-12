import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(dotenv_path=f'{Path(__file__).parents[2]}/.env.prod')

DB_LOGIN = os.getenv("LOGIN")
DB_PASSWORD = os.getenv("PASSWORD")
DB_DATABASE = os.getenv("DATABASE")
DB_HOST = os.getenv("HOST")
