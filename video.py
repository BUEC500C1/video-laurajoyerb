import threading
import time

def get_feed():
    # Function to get twitter feed from api
    time.sleep(1)
    print(".", end="")
    return

if __name__ == "__main__":
    # Create threads
    feed1 = threading.Thread(target=get_feed)
    feed2 = threading.Thread(target=get_feed)

    feed1.start()
    feed2.start()

    feed1.join()
    feed2.join()

    print("\nDone!")
