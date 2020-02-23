# Twitter Summarizer
video-laurajoyerb created by GitHub Classroom

##### by Laura Joy Erb
##### Professor Osama Alshaykh
##### EC500: Building Software

## Goals
 - Develop a queue system that can exercise your requirements with stub functions
 - Develop the twitter functionality with an API
 - Integrate the twitter functionality with the queue system
 - Actively use CB and CI during development

## Summary
This API receives the user name for a twitter page and returns a video summarizing the last 24 hours of tweets from that user's timeline.

Each tweet is converted to text on a frame, and any media is added to the frame as well. Each frame is shown for 3 seconds. The resulting video is returned to the requesting process.

If the specified user either does not exist or does not have any tweets on their timeline, the resulting video will be a single frame that has the text "This user has no tweets".

For each call, each tweet from the timeline is saved as a separate image in the directory. In order to keep the directory generally clean, the `clean_old()` function will scan all of the calls in the `processes` list, and will clear all .png files associated with calls that have already been completed. The `clean_old()` function is called every time the API receives a new incoming call.

### How to Run
Insert your api keys and tokens in the keys.py file before running the video.py file.

In your local terminal, run `python3 video.py`. The local host will start running and will direct you to go to a link.

In your browser, the welcome page will show.

#### Routes
`/tweets/` will show the default page showing the twitter summary for National Geographic.

`/tweets/?user_name=NatGeo` will show the twitter video summary for a specific user_name

`/progress/` will show the current progress of all requests, including their ID, user name being requested, and the completion status

## Parallel Execution
This API is capable of supporting multiple parallel calls. Upon calling the API (through the `/tweets/` route), the call is added to the processing queue, `q`, as well as the global list of all requests, called `processes`. The queue contains information about the unique id associated with the request, the user name to be searched, and the completion status. When the call is first added to the processing queue, the status is set to "queued".

Four independent threads are used to execute requests. The number of threads is based on the assumption of the machine having four cores capable of processing api calls. The threads all execute the `get_tweets` function. In this function, the thread `.get()` a call from the processing queue, and it does all of the processing required to produce the twitter summary video. Once it has completed, it marks the status of that call as "completed", and it finishes with a `.task_done()` call on the processing queue. This process exists in an infinite loop, so all threads are continually checking for any work to be processed on the queue.

On the Flask side of things, the `/tweets/` route will return the result of the `send_completed_video()` function. This function busy waits until the status of the given request is marked as "complete", meaning that the video has been created and can be sent back to the requester.

## References:
- https://www.earthdatascience.org/courses/earth-analytics-python/using-apis-natural-language-processing-twitter/get-and-use-twitter-data-in-python/
- https://hamelot.io/visualization/using-ffmpeg-to-convert-a-set-of-images-into-a-video/
