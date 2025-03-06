import json
import concurrent.futures
from main import Booker  # Replace with the actual filename of your main script

def load_users(json_file):
    with open(json_file, "r") as f:
        return json.load(f)

def process_user(user_id, user_data):
    username = user_data["USERNAME"]
    password = user_data["PASSWORD"]
    dates = user_data["DATES"]

    print(f"Processing user {user_id} with username {username}")
    
    booker = Booker(username, password, user_id, dates)  # Assuming Booker takes username & password
    booker.search()  # Assuming search() method exists in Booker

def run_search_for_users(json_file):
    users = load_users(json_file)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
        futures = {executor.submit(process_user, user_id, user_data): user_id for user_id, user_data in users.items()}
        
        for future in concurrent.futures.as_completed(futures):
            user_id = futures[future]
            try:
                future.result()  # This will raise any exceptions encountered in the thread
            except Exception as e:
                print(f"Error processing user {user_id}: {e}")

if __name__ == "__main__":
    run_search_for_users("user_data.json")  # Update the filename as needed
