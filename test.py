import praw

import pandas as pd
import time
import psycopg2

# Connect to the database
conn = psycopg2.connect(
    host='database-1.cueq5a3aruqx.us-east-2.rds.amazonaws.com',
    database='db1',
    user='postgres',
    password='Manonthemoon123'
)

cursor = conn.cursor()

create_table_query = '''
    CREATE TABLE IF NOT EXISTS avg_price (
        category VARCHAR(255),
        price DECIMAL(10, 2)
    )
'''

try:
    cursor.execute(create_table_query)
    print("Table 'avg_price' created successfully!")
except psycopg2.Error as err:
    print(f"Error creating table: {err}")

conn.commit()
cursor.close()
conn.close()
