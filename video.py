import threading
import queue
import time
import datetime

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
# OAuth process, using the keys and tokens
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tw.API(auth)

date = datetime.date.today() - datetime.timedelta(days=1)

for status in tw.Cursor(api.user_timeline, screen_name='@NatGeo', tweet_mode="extended", since=date, until=date).items(50):
    print(status.full_text)
    print("\n\n")

q.join()
print("Done!")
