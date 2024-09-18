import json
import subprocess
import time


def load_users():
    try:
        with open('../user_data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
USER = load_users()
print(USER)
command = [
    'python', 'type2.py',
    '--date', json.dumps(USER['587628950']['DATES']),
    '--chatid', '587628950'
]

#creationflags = subprocess.CREATE_NEW_CONSOLE
process = subprocess.Popen(command,creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,start_new_session=True)

time.sleep(10)