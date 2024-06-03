import os

from dotenv import load_dotenv
from psycopg2 import pool
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

conn_pull = psycopg2.pool.SimpleConnectionPool(1, 20, DATABASE_URL)
