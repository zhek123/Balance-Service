# config.py
import os

from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
ASYNC_DATABASE_URI = os.getenv("ASYNC_DATABASE_URI")
class Config:
    DEBUG = DEBUG
    HOST = HOST
    PORT = int(PORT)
    DATABASE_URI = ASYNC_DATABASE_URI
