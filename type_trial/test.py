import sys
import contextlib
import logging

log_file_path = 'trial.log'

# Configure logging to only write to the log file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
    ]
)

# Define a custom print function that logs messages and prints to console
def print(*args, **kwargs):
    message = ' '.join(map(str, args))
    logging.info(message)
    __builtins__.print(message, **kwargs)

# Open the log file in append mode and redirect stdout and stderr
with open(log_file_path, 'a') as log_file:
    with contextlib.redirect_stdout(log_file), contextlib.redirect_stderr(log_file):
        # Your script goes here
        # print("This is a standard output message.")
        sys.stdout.flush()
        # logging.info("This is an info message.")
        # try:
        #     raise Exception("This is an error message.")
        # except Exception as e:
        #     logging.error("An error occurred", exc_info=True)

# Include the final print statement
print('hello')
