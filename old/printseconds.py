import threading
import time

# Global variable to control the print_seconds function
stop_flag = False

def print_seconds():
    global stop_flag
    start_time = time.time()
    while not stop_flag:
        elapsed_time = int(time.time() - start_time)
        if elapsed_time >= 60:
            break
        print(f"{elapsed_time} seconds")
        time.sleep(1)

def restart_print_seconds(x):
    global stop_flag
    while True:
        stop_flag = False
        t = threading.Thread(target=print_seconds)
        t.start()
        time.sleep(x)
        stop_flag = True
        t.join()  # Wait for the thread to finish before restarting

# Example usage
# This will restart the print_seconds function every 30 seconds
restart_print_seconds(30)
