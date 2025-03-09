import requests
def SendNotification(text):
        people_msg = [
            "https://api.callmebot.com/text.php?user=@JoelPP&text=",
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

SendNotification("Hello World")