from video import send_completed_video
from video import format_tweet_text, dated_tweets, add_media, no_tweets_error
from video import get_tweet_images, get_tweets
from video import clean_all, clean_old

import os

import globals

# def test1():
#     # setup
#     globals.init()

#     call = {
#         "user_name": "NatGeo",
#         "id": 0,
#         "status": "queued"
#     }
#     globals.q.put(call)
#     globals.processes["0"] = call

#     # get_tweets()

#     # assert globals.processes["0"]["status"] == "completed"
#     assert 1 == 1

def test_error_image():
    no_tweets_error("LauraJoy", "314")

    file_exists = os.path.isfile(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/314LauraJoy_tweet0.png")

    if file_exists:
        os.remove("/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/314LauraJoy_tweet0.png")

    assert file_exists == True

def test_clean_all():
    # creates a bunch of png and mp4 files to be cleaned
    for i in range(10):
        os.system("touch myfile" + str(i) + ".png")
        os.system("touch myfile" + str(i) + ".mp4")

    # creates other miscellaneous files that should not be deleted
    os.system("touch pngfile.txt")
    os.system("touch pngfile.pdf")

    clean_all()

    any_exist = False;
    for j in range(10):
        if os.path.isfile(
            "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/myfile" + str(j) + ".png"):
                any_exist = True

    missing_txt = os.path.isfile(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/pngfile.txt") == False
    missing_pdf = os.path.isfile(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/pngfile.pdf") == False

    assert any_exist == False
    assert missing_txt == False
    assert missing_pdf == False

    os.remove(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/pngfile.txt")
    os.remove(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/pngfile.pdf")

def test_clean_specific_none():
    # creates a bunch of png and mp4 files to be cleaned
    for i in range(10):
        os.system("touch 0NatGeo" + str(i) + ".png")
        os.system("touch NatGeo" + str(i) + ".mp4")

    # setup
    globals.init()

    call = {
        "user_name": "NatGeo",
        "id": 0,
        "status": "queued"
    }
    globals.q.put(call)
    globals.processes["0"] = call

    # no processes are "completed" so no files should be deleted
    clean_old()

    assert os.path.isfile(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/0NatGeo0.png")
    assert os.path.isfile(
        "/Users/laurajoyerb/Documents/MyCode/EC500/video-laurajoyerb/NatGeo0.mp4")

