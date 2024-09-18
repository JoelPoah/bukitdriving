
import argparse
from datetime import datetime
from multiprocessing import Event, Process
import os
import sys
import threading
import time
import requests

TOKEN = '7478425020:AAEHGNgDqa590x2xq6bHjMwgorv2F2Nc-D4'


def book_function(chatid, username, password, dates, stop_event):
    
    # count from 0 to x seconds 
    for i in range(20):
        SendNotification(f"Counting {i} at {str(datetime.now())}", chatid)
        time.sleep(1)
    
    # the thing never ends so no stop_event.set() is called


def SendNotification(text,chatid):
    people_msg = [
    f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chatid}&text='
    ]
    max_chunk_size = 1000  # Maximum characters per batch
    length_of_text = len(text)
    current_index = 0
    while current_index < length_of_text:
        # Determine the end index for the current batch
        end_index = min(current_index + max_chunk_size, length_of_text)
        # Extract the current chunk of text
        current_chunk = text[current_index:end_index]
        #Sends the message
        for i in people_msg:
            url = i + current_chunk
            requests.post(url)
        # Move to the next chunk
        current_index = end_index 



# def run_periodically(interval, func, chatid, username, password, dates):
#     stop_event = Event()
#     dates_eval = eval(dates)  # Ensure 'dates' is evaluated safely or refactor this part
#     process = Process(target=func, args=(chatid, username, password, dates_eval, stop_event))
    
#     SendNotification(f"Starting the process at {datetime.now()}", chatid)
#     process.start()
    
#     # Allow the process to run for the specified interval
#     process.join(interval)
    
#     # If the process is still running after the interval, terminate it
#     if process.is_alive():
#         SendNotification(f"Terminating the process at {datetime.now()}", chatid)
#         stop_event.set()  # Signal the process to stop
#         process.terminate()
#         process.join(2)  # Ensure the process has finished
#         restart_program(chatid)

# def restart_program(chatid):
#     """Restarts the current program."""
#     python = sys.executable
#     os.execl(python, python, *sys.argv)


def run_periodically(interval, func, chatid, username, password, dates):
    stop_event = Event()
    dates_eval = eval(dates)  # Ensure 'dates' is evaluated safely or refactor this part
    process = Process(target=func, args=(chatid, username, password, dates_eval, stop_event))
    
    SendNotification(f"Starting the process at {datetime.now()}", chatid)
    process.start()
    
    # Allow the process to run for the specified interval
    process.join(interval)
    
    # If the process is still running after the interval, terminate it
    if process.is_alive():
        SendNotification(f"Terminating the process at {datetime.now()}", chatid)
        stop_event.set()  # Signal the process to stop
        process.terminate()
        process.join()  # Ensure the process has finished
    
    # Restart the program only if the process was terminated
    if stop_event.is_set() and not process.is_alive():
        restart_program(chatid)

def restart_program(chatid):
    """Restarts the current program."""
    SendNotification("Restarting the process...", chatid)
    python = sys.executable
    os.execl(python, python, *sys.argv)



    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send notifications to chatid")
    parser.add_argument('--chatid', type=str, required=True, help='Send to Specific ChatID')
    parser.add_argument('--username', type=str, required=True, help='Username for BBDC')
    parser.add_argument('--password', type=str, required=True, help='Password for BBDC')
    parser.add_argument('--dates', type=str, required=True, help='Dates for BBDC')
    args = parser.parse_args()
    interval = 10  # Interval in seconds
    
    run_periodically(interval, book_function, args.chatid, args.username, args.password, args.dates)
    
# python test.py --chatid 587628950 --username 105F26022004 --password 020975 --dates "[32]"