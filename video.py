import threading
import queue
import time

q = queue.Queue(maxsize=5)

def callback():
    print("A thread has finished")

def get_feed(q, i, callback):
    while True:
        foo = q.get()
        time.sleep(0.5)
        print(foo, end=", from thread ")
        print(i)
        q.task_done()
        callback()

def queue_module(index):
    q.put(index)
    worker = threading.Thread(target=get_feed, args=(q, index, callback))
    index += 1
    worker.setDaemon(True)
    worker.start()

# Main
for val in range(20):
    queue_module(val)

q.join()
print("Done!")
