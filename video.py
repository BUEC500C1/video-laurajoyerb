import datetime
import math
import requests
import shutil
import pickle

import os
import tweepy as tw

from flask import send_file

from PIL import Image, ImageDraw
from io import BytesIO

# imports global variables
import globals

no_keys = False

try:
    shutil.copy('keys', 'keys.py')
    from keys import *
except:
    no_keys = True


def send_completed_video(ident):
    # waits for video to be completed
    while globals.processes[ident]["status"] != "completed":
        pass

    # returns video file to original process request
    return send_file(str(ident) + globals.processes[ident]["user_name"] + "_twitter_video.mp4")


def format_tweet_text(text):
    # if full text is longer than 25 characters, add a new line so it wraps
    if len(text) > 25:
        res = '\n'.join(text[i:i + 25] for i in range(0, len(text), 25))
        lines = math.ceil(len(text) / 25)
        return res, lines
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
    if not no_keys:
        # OAuth process, using the keys and tokens
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Creation of the actual interface, using authentication
        api = tw.API(auth)

    # infinite while loop for threads
    while True:
        video_request = globals.q.get()
        ident = video_request["id"]
        user_name = video_request["user_name"]

        globals.processes[str(ident)]["status"] = "processing"

        if no_keys:
            default_tweets = open("allTweets.obj", "rb")
            raw_tweets = default_tweets.read()
            allTweets = pickle.loads(raw_tweets)
            day_tweets = dated_tweets(allTweets)
            # creates all images and stores them as png files in the directory
            get_tweet_images(day_tweets, user_name, ident)
        else:
            try:
                allTweets = api.user_timeline(screen_name=user_name, tweet_mode="extended", count=100)
            except:
                no_tweets_error(user_name, ident)
            else:
                day_tweets = dated_tweets(allTweets)

                # creates and stores images as png files in the directory
                get_tweet_images(day_tweets, user_name, ident)

        # creates video using ffmpeg
        os.system(
            "ffmpeg -r 1/3 -f image2 -s 174x300 -i " + str(ident) + user_name + "_tweet%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p " + str(ident) + user_name + "_twitter_video.mp4")

        globals.processes[str(ident)]["status"] = "completed"
        globals.q.task_done()


# removes all previous tweets, images, and videos
def clean_all():
    for file in os.listdir('.'):
        if file.endswith('.png') or file.endswith('.mp4'):
            os.remove(file)


# cleans all old images out (videos stay)
def clean_old():
    for call in globals.processes.values():
        if call["status"] == "completed":
            for file in os.listdir('.'):
                if file.startswith(str(call["id"]) + call["user_name"]) & file.endswith('.png'):
                    os.remove(file)


# globals.init()

# call = {
#     "user_name": "NatGeo",
#     "id": 0,
#     "status": "queued"
# }
# globals.q.put(call)
# globals.processes["0"] = call

# get_tweets()
