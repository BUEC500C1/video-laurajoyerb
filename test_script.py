from video import format_tweet_text, dated_tweets, no_tweets_error
from video import get_tweet_images, get_tweets
from video import clean_all, clean_old

import os
import threading
import time
import pickle

import globals


def add_call(name="NatGeo", ident=0, status="queued"):
    globals.init()

    call = {
        "user_name": name,
        "id": ident,
        "status": status
    }
    globals.q.put(call)
    globals.processes["0"] = call


def test_processes_status():
    add_call()

    # calls get_tweets function
    # must be done in a thread because the function runs in an infinite loop
    worker = threading.Thread(target=get_tweets)
    worker.setDaemon(True)
    worker.start()

    assert globals.processes["0"]["status"] == "processing"
    time.sleep(3)
    assert globals.processes["0"]["status"] == "completed"


def test_image_creation():
    default_tweets = open("allTweets.obj", "rb")
    raw_tweets = default_tweets.read()
    allTweets = pickle.loads(raw_tweets)
    day_tweets = dated_tweets(allTweets)

    get_tweet_images(day_tweets, "LauraJoy", 314)

    for i in range(0, len(day_tweets)):
        assert os.path.isfile("314LauraJoy_tweet" + str(i) + ".png")
        os.remove("314LauraJoy_tweet" + str(i) + ".png")


def test_format_long_text():
    txt = "123456789.........20...25...30"  # 30 chars long
    short, lines = format_tweet_text(txt)

    assert lines == 2
    assert short[24] == "5"
    assert short[25] == "\n"
    assert short[26] == "."


def test_format_short_text():
    txt = "123456789.........20...25"  # 25 chars long
    short, lines = format_tweet_text(txt)

    assert lines == 1
    assert short[24] == "5"
    assert len(short) == 25


def test_format_50_text():
    # 50 chars long
    txt = "123456789.........20...25123456789.........20...50"
    short, lines = format_tweet_text(txt)

    assert lines == 2
    assert short[24] == "5"
    assert short[25] == "\n"
    assert short[26] == "1"
    assert len(short) == 51


def test_error_image():
    no_tweets_error("LauraJoy", "314")

    file_exists = os.path.isfile(
        "314LauraJoy_tweet0.png")

    if file_exists:
        os.remove("314LauraJoy_tweet0.png")

    assert file_exists


def test_clean_all():
    # creates a bunch of png and mp4 files to be cleaned
    for i in range(10):
        os.system("touch myfile" + str(i) + ".png")
        os.system("touch myfile" + str(i) + ".mp4")

    # creates other miscellaneous files that should not be deleted
    os.system("touch pngfile.txt")
    os.system("touch pngfile.pdf")

    clean_all()

    any_exist = False
    for j in range(10):
        if os.path.isfile("myfile" + str(j) + ".png"):
            any_exist = True

    missing_txt = not os.path.isfile("pngfile.txt")
    missing_pdf = not os.path.isfile("pngfile.pdf")

    assert not any_exist
    assert not missing_txt
    assert not missing_pdf

    os.remove("pngfile.txt")
    os.remove("pngfile.pdf")


def test_clean_specific_none():
    # creates a bunch of png and mp4 files to be cleaned
    for i in range(10):
        os.system("touch 0NatGeo" + str(i) + ".png")
        os.system("touch NatGeo" + str(i) + ".mp4")

    add_call()

    # no processes are "completed" so no files should be deleted
    clean_old()

    assert os.path.isfile("0NatGeo0.png")
    assert os.path.isfile("NatGeo0.mp4")

    for i in range(10):
        os.remove("0NatGeo" + str(i) + ".png")
        os.remove("NatGeo" + str(i) + ".mp4")


def test_clean_specific():
    # creates a bunch of png and mp4 files to be cleaned
    for i in range(10):
        os.system("touch 0NatGeo" + str(i) + ".png")
        os.system("touch 0NatGeo" + str(i) + ".mp4")

    add_call(status="completed")

    # process is "completed" so png files should be deleted
    clean_old()

    # clean_old deletes tweet images, but not the tweet video
    assert not os.path.isfile("0NatGeo0.png")
    assert os.path.isfile("0NatGeo0.mp4")

    for i in range(10):
        os.remove("0NatGeo" + str(i) + ".mp4")
