#!/bin/bash

run_window_main() {
    if [ -z "$JOEL_PID" ] || ! kill -0 $JOEL_PID 2>/dev/null; then
        echo "Starting ryan.py..."
        python print.py &
        JOEL_PID=$!
    else
        echo "ryan.py is already running with PID $JOEL_PID."
    fi
}

terminate_process() {
    if [ -n "$JOEL_PID" ] && kill -0 $JOEL_PID 2>/dev/null; then
        echo "Terminating ryan.py with PID $JOEL_PID..."
        kill -TERM $JOEL_PID
        wait $JOEL_PID
        JOEL_PID=""  # Clear the PID
    else
        echo "Process not running or already terminated."
    fi
}

run=true
JOEL_PID=""

while $run; do
    # Get the current hour and minute
    current_hour=$(date +%H)
    current_minute=$(date +%M)

    # Calculate the current time in minutes since midnight
    current_time=$((10#$current_hour * 60 + 10#$current_minute))

    # Define restricted time windows in minutes since midnight
    restricted_times=(
        $((2 * 60 + 30)) $((3 * 60 + 30))  # 2:30 AM - 3:30 AM
        $((7 * 60 + 31)) $((11 * 60))  # 7:47 AM - 7:48 AM
        $((18 * 60 ))     $((19 * 60 + 30)) # 6:00 PM - 7:30 PM
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
        run_window_main  # Start process if not running
        # Sleep for a short interval to ensure timely rechecks
        sleep 30
    fi

    # Check for a stop signal
    if [ -f ./stop_signal.txt ]; then
        echo "Stop signal received. Terminating..."
        terminate_process
        rm -f ./stop_signal.txt
        run=false
    fi
done
