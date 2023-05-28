import psycopg2
import csv
import boto3
from datetime import date
import config
conn = psycopg2.connect(
    host=config.pg_host,
    database=config.pg_database,
    user=config.pg_user,
    password=config.pg_password
)
cur = conn.cursor()

query = "SELECT category AS Category, AVG(price) AS Price FROM public.gundeals GROUP BY category"
cur.execute(query)

rows = cur.fetchall()

current_date = date.today().strftime("%Y-%m-%d")

csv_filename = f"gundeals_average_prices_{current_date}.csv"

with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([desc[0] for desc in cur.description]) 
    writer.writerows(rows)  

s3 = boto3.client(
    's3',
    aws_access_key_id='AKIAULBW5F545X3NIB54',
    aws_secret_access_key='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',
    region_name='us-east-2' 
)

bucket_name = "gundealsbucket1"
s3.upload_file(csv_filename, bucket_name, csv_filename)

cur.close()
conn.close()

print(f"CSV file '{csv_filename}' uploaded to S3 bucket '{bucket_name}' successfully.")
