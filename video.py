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

# unique identifier for each process
id = 0

# global queue for calling processes
q = queue.Queue(maxsize=50)

# global dict for tracking completion status of requests
processes = {}

def send_completed_video(ident):
    # waits for video to be completed
    while processes[ident]["status"] != "completed":
        pass
    
    # returns video file to original process request
    return send_file(processes[ident]["user_name"] + "_twitter_video.mp4")

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

def no_tweets_error(user_name, ident):
    error_image = Image.new('RGB', (203, 350), (255, 255, 255))
    d = ImageDraw.Draw(error_image)
    d.text((15, 10), "This user has no tweets", fill=(0, 0, 0))

    error_image.thumbnail((300, 300), Image.ANTIALIAS)

    # saves the image
    image_name = str(ident) + user_name + "_tweet0.png"
    error_image.save(image_name)

def get_tweet_images(tweets, user_name, ident):
    if len(tweets) == 0:
        no_tweets_error(user_name, ident)

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
        image_name = str(ident) + user_name + "_tweet" + str(index) + ".png"
        text_img.save(image_name)
        index += 1

def get_tweets():

    # OAuth process, using the keys and tokens
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Creation of the actual interface, using authentication
    api = tw.API(auth)

    while True:
        video_request = q.get()
        ident = video_request["id"]
        user_name = video_request["user_name"]

        processes[str(ident)]["status"] = "processing"

        try:
            allTweets = api.user_timeline(screen_name=user_name,
                                        tweet_mode="extended", count=100)
        except:
            no_tweets_error(user_name, ident)
        else:
            day_tweets = dated_tweets(allTweets)

            # creates all images and stores them as png files in the directory
            get_tweet_images(day_tweets, user_name, ident)

        # creates video using ffmpeg
        os.system(
            "ffmpeg -r 1 -f image2 -s 174x300 -i " + str(ident) + user_name + "_tweet%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p " + user_name + "_twitter_video.mp4")

        processes[str(ident)]["status"] = "completed"
        q.task_done()

# removes all previous tweets, images, and videos
def clean_all():
    for file in os.listdir('.'):
        if file.endswith('.png') or file.endswith('.mp4'):
            os.remove(file)

# cleans all old images out (videos stay)
def clean_old():
    for call in processes.values():
        if call["status"] == "completed":
            for file in os.listdir('.'):
                if file.startswith(str(call["id"]) + call["user_name"]) & file.endswith('.png'):
                    os.remove(file)

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Twitter Video Project</h1><p>by Laura Joy Erb</p><p>for EC500: Building Software</p>"

@app.route('/tweets/', methods=['GET'])
def twitter_username():
    # used to periodically clean out unnecessary files
    # cleaning will increase in frequency as calls become more frequent
    clean_old()

    global id

    # default user name if none provided
    name = "NatGeo"

    if 'username' in request.args:
        name = request.args['username']
 
    call = {
        "user_name": name,
        "id": id,
        "status" : "queued"
    }
    ident = str(id)
    id += 1

    # adds to dict of all process requests
    processes[ident] = call

    # adds to worker queue to be completed
    q.put(call)

    q.join()

    return send_completed_video(ident)


if __name__ == '__main__':
    # resets
    id = 0
    clean_all()
    processes.clear()

    q.join()

    # creates and starts threads
    worker = threading.Thread(target=get_tweets)
    worker.setDaemon(True)
    worker.start()

    # begins app
    app.run()
