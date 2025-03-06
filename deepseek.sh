#!/bin/bash

# Lock file to prevent overlapping processes
LOCK_FILE="/tmp/search_users.lock"
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "Script is already running."; exit 1; }

# Function to start search_users.py
run_window_main() {
    if [ -z "$SEARCH_PID" ] || ! kill -0 "$SEARCH_PID" 2>/dev/null; then
        echo "Starting search_users.py..."
        python search_users.py &
        SEARCH_PID=$!
        last_restart_time=$(date +%s)  # Update last restart timestamp
    else
        echo "search_users.py is already running with PID $SEARCH_PID."
    fi
}

# Function to terminate search_users.py
terminate_process() {
    if [ -n "$SEARCH_PID" ] && kill -0 "$SEARCH_PID" 2>/dev/null; then
        echo "Terminating search_users.py with PID $SEARCH_PID..."
        kill -TERM "$SEARCH_PID"
        wait "$SEARCH_PID"
        SEARCH_PID=""  # Clear the PID
    else
        echo "Process not running or already terminated."
    fi
}

# Trap to ensure cleanup on script exit
trap 'terminate_process; rm -f "$LOCK_FILE"; exit' INT TERM EXIT

# Main loop
run=true
SEARCH_PID=""
last_restart_time=$(date +%s)  # Initialize restart timestamp

while $run; do
    # Get the current hour and minute
    current_hour=$(date +%H)
    current_minute=$(date +%M)

    # Calculate the current time in minutes since midnight
    current_time=$((10#$current_hour * 60 + 10#$current_minute))

    # Define restricted time windows in minutes since midnight
    restricted_times=(
        $((23 * 60 + 30)) $((24 * 60))  # 11:30 PM - 12 AM
        $((0 * 60)) $((13 * 60 + 30))  # 12 AM - 1:30 PM
        $((16 * 60 + 30)) $((17 * 60 + 30))  # 4:30 PM - 5:30 PM
        $((18 * 60 + 30)) $((19 * 60 + 30))  # 6:30 PM - 7:30 PM
    )

    # Check if the current time is within a restricted time window
    in_restricted="false"
    for ((i = 0; i < ${#restricted_times[@]}; i += 2)); do
        start_time=${restricted_times[i]}
        end_time=${restricted_times[i + 1]}
        if (( current_time >= start_time && current_time < end_time )); then
            in_restricted="true"
            break
        fi
    done

    if [ "$in_restricted" = "true" ]; then
        echo "Restricted time: $current_time minutes. Terminating process if running..."
        terminate_process
        sleep 60  # Wait before rechecking
    else
        current_time_secs=$(date +%s)
        elapsed_time=$((current_time_secs - last_restart_time))
        
        if (( elapsed_time >= 1300 )); then
            echo "1300 seconds elapsed since last restart. Restarting search_users.py..."
            terminate_process
            run_window_main
        else
            run_window_main  # Start process if not running
        fi
        
        sleep 30  # Sleep for a short interval to ensure timely rechecks
    fi

    # Check for a stop signal
    if [ -f /path/to/stop_signal.txt ]; then  # Use absolute path
        echo "Stop signal received. Terminating..."
        terminate_process
        rm -f /path/to/stop_signal.txt
        run=false
    fi
done