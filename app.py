import praw
import pandas as pd
import time
import psycopg2

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

# Create table if it doesn't exist
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
        # Extract first word from post title and stop at ']'
        category = ''
        for char in post.title:
            if char == ']':
                break
            elif char != ' ':
                category += char
        post_data['Category'] = category[1:] if category else None  # Remove first character of the first word

        # Extract price from post title
        price = None
        if '$' in post.title:
            price_start = post.title.index('$') + 1
            price_end = post.title.find(' ', price_start)
            if price_end == -1:
                price_end = len(post.title)
            price_str = post.title[price_start:price_end]
            price_str = price_str.replace(',', '')  # Remove commas from price string
            if 'K' in price_str:
                price = int(float(price_str[:-1]) * 1000)
            else:
                price = float(price_str)
        post_data['Price'] = price

        data.append(post_data)

    df = pd.DataFrame(data)
    print(posts)
    print(df)  # You can modify this part to perform any desired operations with the dataframe

    # Insert data into the database
    for post in data:
        # Fetch price and category from post data
        price = post['Price']
        category = post['Category']

        cur.execute("""
            INSERT INTO gundeals (id, title, post_time, url, price, category)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (post['Post ID'], post['Post Title'], post['Post Time'], post['Post Link'], price, category))

    # Commit the changes and close the database connection
    conn.commit()

    time.sleep(600)  # Sleep for 10 minutes before collecting the next set of posts

cur.close()
conn.close()
