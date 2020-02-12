import threading
import queue
import time

q = queue.Queue(maxsize=5)

def get_feed(q, i):
    while True:
        foo = q.get()
        time.sleep(0.5)
        print(foo, end=", from thread ")
        print(i)
        q.task_done()

def queue_module(index):
    q.put(index)
    worker = threading.Thread(target=get_feed, args=(q,index))
    index += 1
    worker.setDaemon(True)
    worker.start()

queue_module(1)
queue_module(2)
queue_module(3)

q.join()
print("Done!")
