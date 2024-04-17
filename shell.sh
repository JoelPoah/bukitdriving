#!/bin/bash

# Function to run the Python script and kill it after 10 minutes
run_python_script() {
    # Activate the virtual environment
    # C:/Users/Admin/Desktop/BBDC/venv/Scripts/activate
    # Run Python script in the background
    python3 main.py &

    # Save the process ID of the Python script
    PYTHON_PID=$!
    CHROMEID1=$(pgrep -n "Google Chrome")

    # Kill the Python script`
    kill $PYTHON_PID
    kill $CHROMEID1
    # echo "Python script killed"
    echo "Python script killed"

    #!/bin/bash

}

# Run the Python script every 20 minutes
while true; do
    # Call the function to run the Python script
    run_python_script

    # Sleep for 30sec before running again
    sleep 360
done




