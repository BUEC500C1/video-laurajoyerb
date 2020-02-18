import threading
import queue
import time

import os
import tweepy as tw
import pandas as pd

from config import consumer_key
from config import consumer_secret
from config import access_token
from config import access_token_secret

q = queue.Queue(maxsize=5)

def callback():
    print("A thread has finished")

def get_feed(q, i, callback):
    while True:
        foo = q.get()
        time.sleep(0.5)
        # print(foo, end=", from thread ")
        # print(i)
        q.task_done()
        callback()

def queue_module(index):
    q.put(index)
    worker = threading.Thread(target=get_feed, args=(q, index, callback))
    index += 1
    worker.setDaemon(True)
    worker.start()


# Main
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

# Define the search term and the date_since date as variables
search_words = "#wildfires"
date_since = "2018-11-16"

# Collect tweets
tweets = tw.Cursor(api.search,
                   q=search_words,
                   lang="en",
                   since=date_since).items(5)

for val in range(20):
    queue_module(val)

all_tweets = [tweet.text for tweet in tweets]
print(all_tweets[:5])

q.join()
print("Done!")
