import argparse
from datetime import datetime
import json
import time

import requests


TOKEN = '7478425020:AAEHGNgDqa590x2xq6bHjMwgorv2F2Nc-D4'
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test for type2.py")
    parser.add_argument('--dates', type=str, required=True, help='Dates for BBDC')
    parser.add_argument('--chatid', type=str, required=True, help='Chat ID for Telegram')
    args = parser.parse_args()
    
    SendNotification(f"Starting the type trial at {datetime.now()}", args.chatid)
    SendNotification(f"Dates: {args.dates}", args.chatid)
    SendNotification(f"Type of dates: {type(args.dates)}", args.chatid)
    
    # after dumping the dates type:
    dates = eval(args.dates)
    SendNotification(f"Dates after dumping: {dates}", args.chatid)
    SendNotification(f"Type of dates: {type(dates)}", args.chatid)
    
    time.sleep(10)
