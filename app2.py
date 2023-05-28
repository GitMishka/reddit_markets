import praw
import pandas as pd
import time
import psycopg2
from twilio.rest import Client

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
       
        # Add your code here to handle price and category extraction
        # ...

        data.append(post_data)

        # If post title contains an item from the list, send a link via Twilio
        if any(item in post.title for item in items_to_search):
            message = twilio_client.messages.create(
                body=f"New post found: {post.url}",
                from_=twilio_phone_number,
                to="14232272113"
            )

    df = pd.DataFrame(data)

    # Add your code here to store posts data into the database
    # ...

    time.sleep(600)

cur.close()
conn.close()
