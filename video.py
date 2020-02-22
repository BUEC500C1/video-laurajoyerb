import threading, queue
import time, datetime
import math
import requests
import flask

import os
import tweepy as tw
import pandas as pd

from flask import request, send_file

from PIL import Image, ImageDraw, ImageOps
from io import BytesIO

from config import consumer_key, consumer_secret
from config import access_token, access_token_secret

# global queue for calling processes
q = queue.Queue(maxsize=50)

def get_feed(q, i):
    while True:
        foo = q.get()
        time.sleep(0.5)
        q.task_done()

def queue_module(index):
    q.put(index)
    worker = threading.Thread(target=get_feed, args=(q, index))
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

# pastes tweet media onto tweet image
def add_media(tweet, image, img_height):
    img_url = tweet.entities['media'][0]['media_url_https']
    response = requests.get(img_url)
    media_img = Image.open(BytesIO(response.content))
    media_img.thumbnail((180, 180), Image.ANTIALIAS)
    image.paste(media_img, (10, img_height + 15))

def get_tweet_images(tweets):
    index = 0
    for tweet in tweets:
        # wraps text to fit image
        wrapped_text, new_lines = format_tweet_text(tweet.full_text)

        has_image = True if ('media' in tweet.entities) else False

        # determines appropriate sizing for text part of image
        img_height = 21 * new_lines if new_lines > 4 else 21 * new_lines + 5
        text_img = Image.new('RGB', (203, 350), (255, 255, 255))

        # creates the text image
        d = ImageDraw.Draw(text_img)
        d.text((15, 10), wrapped_text.encode(
            'cp1252', 'ignore'), fill=(0, 0, 0))

        # gets, resizes, and pastes the tweet image if it is present
        if has_image:
            add_media(tweet, text_img, img_height)

        text_img.thumbnail((300, 300), Image.ANTIALIAS)

        # saves the image for later compilation
        image_name = "tweet" + str(index) + ".png"
        text_img.save(image_name)
        index += 1

def get_tweets(user_name):

    # OAuth process, using the keys and tokens
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Creation of the actual interface, using authentication
    api = tw.API(auth)

    allTweets = api.user_timeline(screen_name=user_name,
                                tweet_mode="extended", count=100)

    day_tweets = dated_tweets(allTweets)

    # creates all images and stores them as png files in the directory
    get_tweet_images(day_tweets)

    # creates video using ffmpeg
    os.system(
        "ffmpeg -r 1 -f image2 -s 174x300 -i tweet%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p twitter_video.mp4")

# removes all previous tweets, images, and videos
def clean_all():
    for file in os.listdir('.'):
        if file.endswith('.png') or file.endswith('.mp4'):
            os.remove(file)

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Twitter Video Project</h1><p>by Laura Joy Erb</p><p>for EC500: Building Software</p>"

@app.route('/tweets/', methods=['GET'])
def twitter_username():
    clean_all()
    if 'username' in request.args:
        name = request.args['username']
        get_tweets(name)
    else:
        get_tweets('@NatGeo')

    return send_file("twitter_video.mp4")

app.run()

# # Main
# get_tweets('@NatGeo')

# q.join()
# print("Done!")
