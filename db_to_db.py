import praw
import pandas as pd
import time
import psycopg2


conn = psycopg2.connect(
    host="database-1.cueq5a3aruqx.us-east-2.rds.amazonaws.com",
    database="db1",
    user="postgres",
    password="Manonthemoon123"
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS gundeals_avgprice (
        category TEXT,
        avg_price FLOAT
    )
""")
