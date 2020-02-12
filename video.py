import threading
import queue
import time

def get_feed(q, i):
    while True:
        foo = q.get()
        time.sleep(0.5)
        print(foo, end=", from thread ")
        print(i)
        q.task_done()

q = queue.Queue()
num_threads = 10

for x in range(50):
  q.put(x)

for i in range(num_threads):
  worker = threading.Thread(target=get_feed, args=(q,i))
  worker.setDaemon(True)
  worker.start()

q.join()

print("Done!")
