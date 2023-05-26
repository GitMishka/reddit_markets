import praw
import pandas as pd
import time
import psycopg2


conn = psycopg2.connect(
    host="database-1.cueq5a3aruqx.us-east-2.rds.amazonaws.com",
    database="backup_db",
    user="postgres",
    password="Manonthemoon123"
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS avgprice (
        category TEXT,
        avg_price FLOAT
    )
""")
print(cur.statusmessage)