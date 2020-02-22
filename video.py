import threading
import queue
import time
import datetime
import math
import requests

import os
import tweepy as tw
import pandas as pd

from PIL import Image
from PIL import ImageDraw
from io import BytesIO

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

def dated_tweets(tweets):
    dated = []
    for tweet in tweets:
        # checks if tweet was from the last 24 hours
        if (datetime.datetime.now() - tweet.created_at).days < 1:
            dated.append(tweet)

    return dated

def get_tweets(user_name):

    # OAuth process, using the keys and tokens
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Creation of the actual interface, using authentication
    api = tw.API(auth)

    allTweets = api.user_timeline(screen_name=user_name,
                                tweet_mode="extended", count=100)

    day_tweets = dated_tweets(allTweets)

    index = 0
    for tweet in day_tweets:
        # wraps text to fit image
        wrapped_text, new_lines = format_tweet_text(tweet.full_text)

        has_image = True if ('media' in tweet.entities) else False

        # determines appropriate sizing for text part of image
        img_height = 21 * new_lines if new_lines > 4 else 21 * new_lines + 5
        total_height = (img_height + 200) if has_image else img_height
        text_img = Image.new('RGB', (200, total_height), (255, 255, 255))

        # creates the text image
        d = ImageDraw.Draw(text_img)
        d.text((10, 10), wrapped_text.encode(
            'cp1252', 'ignore'), fill=(0, 0, 0))

        # gets, resizes, and pastes the tweet image if it is present
        if has_image:
            response = requests.get("https://pbs.twimg.com/media/ERFNdgDXsAEVnh_.jpg")
            media_img = Image.open(BytesIO(response.content))
            media_img.thumbnail((180, 180), Image.ANTIALIAS)
            text_img.paste(media_img, (10, img_height + 15))
            print(index)

        # saves the image for later compilation
        image_name = "tweet" + str(index) + ".png"
        text_img.save(image_name)
        index += 1


# Main
get_tweets('@NatGeo')

q.join()
print("Done!")
