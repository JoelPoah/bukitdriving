import time
import requests
import argparse

# chatid = 587628950

# Setting up argument parser
parser = argparse.ArgumentParser(description="Send notifications to chatid")
parser.add_argument('--chatid', type=str, required=True, help='Send to Specific ChatID')
args = parser.parse_args()

people_msg = [
    f'https://api.telegram.org/bot7478425020:AAFtYzoZ2pm4QMq6siIbHWz6nsv-xVYcaoo/sendMessage?chat_id={args.chatid}&text='
]

def SendNotification(text):
    max_chunk_size = 1000  # Maximum characters per batch
    length_of_text = len(text)
    current_index = 0
    while current_index < length_of_text:
        # Determine the end index for the current batch
        end_index = min(current_index + max_chunk_size, length_of_text)
        # Extract the current chunk of text
        current_chunk = text[current_index:end_index]
        # Sends the message
        for i in people_msg:
            url = i + current_chunk
            requests.post(url)
        # Move to the next chunk
        current_index = end_index  

# Include the chatid in the notification messages
SendNotification(f'Started subprocess script for user: {args.chatid}')

time.sleep(10)

SendNotification(f'Finished subprocess script for user: {args.chatid}')
