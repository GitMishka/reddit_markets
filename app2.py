import praw
import pandas as pd
import time
import psycopg2
import requests
from twilio.rest import Client
import config  

def shorten_url(url):
    response = requests.get('http://tinyurl.com/api-create.php?url=' + url)
    return response.text

user_agent = config.reddit_username
reddit = praw.Reddit(
    username=config.reddit_username,
    password=config.reddit_password,
    client_id=config.reddit_client_id,
    client_secret=config.reddit_client_secret,
    user_agent=user_agent,
    check_for_async=False
)

conn = psycopg2.connect(
    host=config.pg_host,
    database=config.pg_database,
    user=config.pg_user,
    password=config.pg_password
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS gundeals (
        id TEXT PRIMARY KEY,
        title TEXT,
        post_time TIMESTAMP,
        url TEXT,
        price FLOAT,
        category TEXT
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS sent_gundeals (
        id TEXT PRIMARY KEY,
        title TEXT,
        post_time TIMESTAMP,
        url TEXT,
        price FLOAT,
        category TEXT
    )
""")

subreddit = reddit.subreddit('gundeals')

twilio_client = Client(config.twilio_account_sid, config.twilio_auth_token)

items_to_search = ["[Handgun]", "item2", "item3"]

while True:
    posts = subreddit.new(limit=10)
    data = []
    for post in posts:
        post_data = {
            'Post Time': pd.to_datetime(post.created_utc, unit='s'),
            'Post Title': post.title,
            'Post ID': post.id,
            'Post Link': post.url
        }
       
        category = ''
        for char in post.title:
            if char == ']':
                break
            elif char != ' ':
                category += char
        post_data['Category'] = category[1:] if category else None 

        price = None
        if '$' in post.title:
            price_start = post.title.index('$') + 1
            price_end = post.title.find(' ', price_start)
            if price_end == -1:
                price_end = len(post.title)
            price_str = post.title[price_start:price_end]
            price_str = price_str.replace(',', '')  
            if 'K' in price_str:
                try:
                    price = int(float(price_str[:-1]) * 1000)
                except ValueError:
                    price = None
            else:
                try:
                    price = float(price_str)
                except ValueError:
                    price = None
        post_data['Price'] = price

        data.append(post_data)

        if any(item in post.title for item in items_to_search):
            short_url = shorten_url(post.url)
            message = twilio_client.messages.create(
                body=f"New post found: {post.title},{short_url},{price}",
                from_=config.twilio_phone_number,
                to=config.twilio_to_number
            )

            cur.execute("""
                INSERT INTO sent_gundeals (id, title, post_time, url, price, category)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (post_data['Post ID'], post_data['Post Title'], post_data['Post Time'], short_url, price, category))

    df = pd.DataFrame(data)
    print(posts)
    print(df)

    for post in data:
        price = post['Price']
        category = post['Category']

        cur.execute("""
            INSERT INTO gundeals (id, title, post_time, url, price, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (post['Post ID'], post['Post Title'], post['Post Time'], post['Post Link'], price, category))

    conn.commit()
    time.sleep(600)

cur.close()
conn.close()
