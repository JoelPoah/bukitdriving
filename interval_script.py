import json
import subprocess
import threading
import httpx
import psutil
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium_stealth import stealth
from random import randint
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
from seleniumwire.utils import decode as sw_decode
import jwt
import sys ,os

from selenium.webdriver.chrome.options import Options
from multiprocessing import Process, Event
import argparse


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
        process.join(5)  # Ensure the process has finished
        
        subprocess_id = process.pid
    
    # Restart the program only if the process was terminated
    if stop_event.is_set() and not process.is_alive():
        time.sleep(10)
        kill_program(chatid,subprocess_id)
        
        
def run_interval(interval, chatid, username, password, dates):
    while True:
        SendNotification("Inside the interval process...", chatid)
        command = [
            'python', 'main.py',
            '--chatid', chatid,
            '--username', username,
            '--password', password,
            '--dates', json.dumps(dates)
        ]
        
        #creationflags = subprocess.CREATE_NEW_CONSOLE
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        #process = subprocess.Popen(command,creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,start_new_session=True)
        SendNotification(f"Process Booking Opened {str(datetime.now())} ", chatid)
        time.sleep(interval)
        
        kill_program(chatid,process.pid)

def kill_program(chatid,subprocess_id):
    """Kill the current program."""
    SendNotification("Killing the process...", chatid)
    try:
        parent = psutil.Process(subprocess_id)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
            parent.kill()
    except psutil.NoSuchProcess:
        SendNotification(f"No process with PID {subprocess_id} was found.", chatid)
        print(f"No process with PID {subprocess_id} was found.")
    except psutil.AccessDenied:
        SendNotification(f"Permission denied to kill process with PID {subprocess_id}.", chatid)
        print(f"Permission denied to kill process with PID {subprocess_id}.")



    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send notifications to chatid")
    parser.add_argument('--chatid', type=str, required=True, help='Send to Specific ChatID')
    parser.add_argument('--username', type=str, required=True, help='Username for BBDC')
    parser.add_argument('--password', type=str, required=True, help='Password for BBDC')
    parser.add_argument('--dates', type=str, required=True, help='Dates for BBDC')
    args = parser.parse_args()
    interval = 600
    
    run_interval(interval, args.chatid, args.username, args.password, args.dates)
    
# flag to take in 
# 1. username
# 2. password
# 3. dates
# 4. SendMessage stuff
# Setting up argument parser



# Set the interval to 3600 seconds (1 hour)
# interval = 3600

# Create and start the thread
# thread = threading.Thread(target=run_periodically, args=(interval, book_function,args.chatid,args.username,args.password,args.dates))
# thread.daemon = True  # Daemonize thread
# thread.start()

# Keep the main program running
# while True:
#     time.sleep(1)
    
# python subbookingprocess.py --chatid 587628950 --username 105F26022004 --password 020975 --dates "[32]"
    
    

# python subbookingprocess.py --chatid 587628950 --username 337a18092001 --password 112220 --dates "[32]"