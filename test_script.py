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

    
