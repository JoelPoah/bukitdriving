#!/bin/bash

SEARCH_PID_FILE="search_users.pid"

run_window_main() {
    if [ -f "$SEARCH_PID_FILE" ]; then
        SEARCH_PID=$(cat "$SEARCH_PID_FILE")
        if kill -0 "$SEARCH_PID" 2>/dev/null; then
            echo "search_users.py is already running with PID $SEARCH_PID."
            return
        fi
    fi

    echo "Starting search_users.py..."
    
    # Activate virtual environment
    if [ -d "./venv" ]; then
        source ./venv/bin/activate || { echo "Failed to activate virtual environment! Exiting..."; exit 1; }
    else
        echo "Virtual environment not found! Exiting..."
        exit 1
    fi

    # Start the process in a new process group
    python search_users.py &  
    SEARCH_PID=$!
    echo "$SEARCH_PID" > "$SEARCH_PID_FILE"
    
    # Make sure the script runs in its own process group
    disown "$SEARCH_PID"
    last_restart_time=$(date +%s)
}

kill_search_processes() {
    echo "Killing all search_users.py processes..."
    pkill -f "search_users.py"

}

terminate_process() {
    if [ -f "$SEARCH_PID_FILE" ]; then
        SEARCH_PID=$(cat "$SEARCH_PID_FILE")
        if kill -0 "$SEARCH_PID" 2>/dev/null; then
            echo "Forcefully killing search_users.py and all child processes..."
            
            # Kill the entire process group
            pkill -P "$SEARCH_PID"  # Kill child processes
            kill -9 "$SEARCH_PID"  # Force kill main process
            
            # Verify if all processes are terminated
            if pgrep -P "$SEARCH_PID" || ps -p "$SEARCH_PID" > /dev/null; then
                echo "Some processes are still running. Trying again..."
                pkill -9 -P "$SEARCH_PID"
                kill -9 "$SEARCH_PID"
            fi

            wait "$SEARCH_PID" 2>/dev/null
            rm -f "$SEARCH_PID_FILE"
        else
            echo "Process not running or already terminated."
            rm -f "$SEARCH_PID_FILE"
        fi
    else
        echo "No PID file found. Process may not be running."
    fi

    # Kill Search processes
    kill_search_processes
}

run=true
last_restart_time=$(date +%s)

while $run; do
    current_hour=$(date +%H)
    current_minute=$(date +%M)
    current_time=$((10#$current_hour * 60 + 10#$current_minute))

    restricted_times=(
        $((23 * 60 + 30)) $((24 * 60))  
        $((0 * 60)) $((13 * 60 + 30))  
        $((16 * 60 + 30)) $((17 * 60 + 30 )) 
        $((18 * 60 + 30)) $((19 * 60 + 30 )) 
    )

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
        sleep 60  
    else
        current_time_secs=$(date +%s)
        elapsed_time=$((current_time_secs - last_restart_time))
        
        if (( elapsed_time >= 1300 )); then
            echo "1300 seconds elapsed since last restart. Restarting search_users.py..."
            terminate_process
            run_window_main
        else
            run_window_main  
        fi
        
        sleep 30  
    fi

    if [ -f "./stop_signal.txt" ]; then
        echo "Stop signal received. Terminating..."
        terminate_process
        rm -f "./stop_signal.txt"
        run=false
    fi
done