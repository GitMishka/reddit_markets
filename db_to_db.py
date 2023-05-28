import praw
import pandas as pd
import time
import psycopg2
import config

conn = psycopg2.connect(
    host=config.pg_host,
    database=config.pg_database,
    user=config.pg_user,
    password=config.pg_password)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS avgprice (
        category TEXT,
        avg_price FLOAT
    )
""")
print(cur.statusmessage)