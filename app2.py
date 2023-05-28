import praw
import pandas as pd
import time
import psycopg2
import requests
from twilio.rest import Client

def shorten_url(url):
    response = requests.get('http://tinyurl.com/api-create.php?url=' + url)
    return response.text

user_agent = "Searchbot_01"
reddit = praw.Reddit(username="Searchbot_01",
                     password="aaaa1111",
                     client_id="Ai32qfXNqvGuMEvHFFMlAw",
                     client_secret="IG5XKjyUGkcG2cgXfBSwVvalMTxFRg",
                     user_agent=user_agent,
                     check_for_async=False)

conn = psycopg2.connect(
    host="database-1.cueq5a3aruqx.us-east-2.rds.amazonaws.com",
    database="postgres",
    user="postgres",
    password="Manonthemoon123"
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

# Add your Twilio details
twilio_account_sid = "ACd2079bd46f13974225b28ef06255af01"
twilio_auth_token = "fc48aa972b023395d213c11a148238c1"
twilio_phone_number = "+18334633894"
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Add your items here
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

        # If post title contains an item from the list, send a link via Twilio and insert into sent_gundeals
        if any(item in post.title for item in items_to_search):
            short_url = shorten_url(post.url)
            message = twilio_client.messages.create(
                body=f"New post found: {short_url}",
                from_=twilio_phone_number,
                to="14232272113"
            )

            # Insert the post into the sent_gundeals table
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
