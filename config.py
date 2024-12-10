import os
from dotenv import load_dotenv
from flask_mysqldb import MySQL


load_dotenv()

mysql = MySQL()
class Config:
    PORT = int(os.getenv("PORT", 3000))
    JWT_SECRET = os.getenv("JWT_SECRET")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
