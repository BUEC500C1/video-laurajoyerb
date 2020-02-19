import threading
import queue
import time
import datetime
import math

import os
import tweepy as tw
import pandas as pd

from PIL import Image
from PIL import ImageDraw

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

def format_tweet_text(text):
    # if full text is longer than 25 characters, add a new line so it wraps
    if len(text) > 25:
        i = 0
        res = '\n'.join(text[i:i + 25] for i in range(0, len(text), 25))
        new_lines = math.floor(len(text) / 25)
        return res, new_lines
    else:
        return text, 1


# Main
# OAuth process, using the keys and tokens
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tw.API(auth)

allTweets = api.user_timeline(screen_name='@NatGeo',
                      tweet_mode="extended", count=100)

index = 0
for tweet in allTweets:
    if (datetime.datetime.now() - tweet.created_at).days < 1:
        print(tweet.full_text)
        print("\n")
        wrapped_text, new_lines = format_tweet_text(tweet.full_text)
        img_height = 20*new_lines if new_lines > 4 else 20*new_lines + 5
        img = Image.new('RGB', (200, img_height), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), wrapped_text.encode(
            'cp1252', 'ignore'), fill=(0, 0, 0))
        image_name = "image" + str(index) + ".png"
        img.save(image_name)
        index += 1

q.join()
print("Done!")
