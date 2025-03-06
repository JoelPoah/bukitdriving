#!/bin/bash

run_window_main() {
    if [ -z "$SEARCH_PID" ] || ! kill -0 $SEARCH_PID 2>/dev/null; then
        echo "Starting search_users.py..."
        python search_users.py &
        SEARCH_PID=$!
        last_restart_time=$(date +%s)  # Update last restart timestamp
    else
        echo "search_users.py is already running with PID $SEARCH_PID."
    fi
}

terminate_process() {
    if [ -n "$SEARCH_PID" ] && kill -0 $SEARCH_PID 2>/dev/null; then
        echo "Terminating search_users.py with PID $SEARCH_PID..."
        kill -TERM $SEARCH_PID
        wait $SEARCH_PID
        SEARCH_PID=""  # Clear the PID
    else
        echo "Process not running or already terminated."
    fi
}

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
        #$((14 * 60 + 30)) $((15 * 60 + 30)) # 2:30 PM - 3:30 PM
        $((16 * 60 + 30)) $((17 * 60 + 30 )) # 4:30pm - 5:30pm
        $((18 * 60 + 30)) $((19 * 60 + 30 )) # 6:30pm - 7:30pm
        #$((20 * 60 + 30)) $((21 * 60 + 30 )) # 8:30pm - 9:30pm
        #$((22 * 60 + 30)) $((23 * 60 + 30 )) # 10:30pm - 11:30pm
        # total 7 hours of non-restricted time
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
    if [ -f ./stop_signal.txt ]; then
        echo "Stop signal received. Terminating..."
        terminate_process
        rm -f ./stop_signal.txt
        run=false
    fi
done
