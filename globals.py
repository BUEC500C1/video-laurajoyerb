import queue


def init():
    global id
    global q
    global processes
    global max_threads

    id = 0  # unique identifier for each process
    q = queue.Queue(maxsize=50)  # global queue for calling processes
    processes = {}  # global dict for tracking completion status of requests
    # number of worker threads to be created (based on # of cores available)
    max_threads = 4
