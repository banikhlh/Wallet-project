import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

DB_PATH = os.getenv("DB_PATH")
TEST_DB_PATH = os.getenv("TEST_DB_PATH")
SECRET_KEY = os.getenv("SECRET_KEY")
LOGGING = os.getenv("LOGGING", "3")
# 1 - console, 2 - file, 3 - both