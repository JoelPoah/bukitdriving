#!/bin/bash

# Function to run the Python script and kill it after 10 minutes
run_python_script() {
    # Activate the virtual environment
    # C:/Users/Admin/Desktop/BBDC/venv/Scripts/activate
    # Run Python script in the background
    python3 main.py &

    # Save the process ID of the Python script
    PYTHON_PID=$!

    # Sleep for 10 minutes browser refreshes and shell will restart after
    sleep 600

    # Kill the Python script`
    kill $PYTHON_PID
    # echo "Python script killed"
    echo "Python script killed"

    #!/bin/bash

    # Get the process IDs (PIDs) of all Chrome instances
    chrome_pids=$(pgrep -i "Google Chrome")

    # Check if Chrome is running
    if [ -z "$chrome_pids" ]; then
      echo "Chrome is not running."
    else
      # Terminate all Chrome processes
      echo "Closing Chrome..."
      kill -15 $chrome_pids
      echo "Chrome closed successfully."
    fi

}

# Run the Python script every 20 minutes
while true; do
    # Call the function to run the Python script
    run_python_script
    # Sleep for 30sec before running again
    sleep 30
done
