#!/bin/bash
set -e  # Exit on error
set -u  # Treat unset variables as an error
set -o pipefail  # Fail on errors in pipelines

# Configuration
SEARCH_PID_FILE="search_users.pid"
STOP_SIGNAL_FILE="stop_signal.txt"
RESTRICTED_TIMES=(
    $((23 * 60 + 30)) $((24 * 60))  # 23:30 - 00:00
    $((0 * 60)) $((13 * 60 + 30))   # 00:00 - 13:30
    $((16 * 60 + 30)) $((17 * 60 + 30))  # 16:30 - 17:30
    $((18 * 60 + 30)) $((19 * 60 + 30))  # 18:30 - 19:30
)
RESTART_INTERVAL=1300  # Restart interval in seconds (1300s = ~21.67 minutes)
SLEEP_INTERVAL=30  # Sleep interval in seconds

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to activate the virtual environment
activate_venv() {
    if [ -d "./venv" ]; then
        log "Activating virtual environment..."
        source ./venv/bin/activate || { log "Failed to activate virtual environment! Exiting..."; exit 1; }
    else
        log "Virtual environment not found! Exiting..."
        exit 1
    fi
}

# Function to start the search_users.py process
start_search_process() {
    log "Starting search_users.py..."
    python search_users.py &
    SEARCH_PID=$!
    echo "$SEARCH_PID" > "$SEARCH_PID_FILE"
    disown "$SEARCH_PID"  # Ensure the process runs independently
    log "search_users.py started with PID $SEARCH_PID."
}

# Function to kill all search_users.py processes
kill_search_processes() {
    log "Killing all search_users.py processes..."
    pkill -f "search_users.py" || true  # Ignore if no processes are found
}

# Function to terminate the search_users.py process and its children
terminate_process() {
    if [ -f "$SEARCH_PID_FILE" ]; then
        SEARCH_PID=$(cat "$SEARCH_PID_FILE")
        if kill -0 "$SEARCH_PID" 2>/dev/null; then
            log "Forcefully killing search_users.py and all child processes..."
            pkill -P "$SEARCH_PID" || true  # Kill child processes
            kill -9 "$SEARCH_PID" || true  # Force kill main process
            wait "$SEARCH_PID" 2>/dev/null || true
            rm -f "$SEARCH_PID_FILE"
        else
            log "Process not running or already terminated."
            rm -f "$SEARCH_PID_FILE"
        fi
    else
        log "No PID file found. Process may not be running."
    fi

    # Kill all Chrome and ChromeDriver processes
    log "Killing all Chrome and ChromeDriver processes..."
    pkill -f "chrome" || true
    pkill -f "chromedriver" || true
}

# Function to check if the current time is within restricted times
is_restricted_time() {
    local current_hour=$(date +%H)
    local current_minute=$(date +%M)
    local current_time=$((10#$current_hour * 60 + 10#$current_minute))

    for ((i = 0; i < ${#RESTRICTED_TIMES[@]}; i += 2)); do
        local start_time=${RESTRICTED_TIMES[i]}
        local end_time=${RESTRICTED_TIMES[i + 1]}
        if (( current_time >= start_time && current_time < end_time )); then
            return 0  # Restricted time
        fi
    done
    return 1  # Not restricted time
}

# Main loop
main() {
    local run=true
    local last_restart_time=$(date +%s)

    while $run; do
        if is_restricted_time; then
            log "Restricted time detected. Terminating process if running..."
            terminate_process
            sleep 60
        else
            local current_time_secs=$(date +%s)
            local elapsed_time=$((current_time_secs - last_restart_time))

            if (( elapsed_time >= RESTART_INTERVAL )); then
                log "Restart interval reached. Restarting search_users.py..."
                terminate_process
                sleep 5  # Wait for resources to be released
                activate_venv
                start_search_process
                last_restart_time=$(date +%s)  # Update restart time
            else
                if [ ! -f "$SEARCH_PID_FILE" ] || ! kill -0 $(cat "$SEARCH_PID_FILE") 2>/dev/null; then
                    log "Process not running. Starting search_users.py..."
                    activate_venv
                    start_search_process
                    last_restart_time=$(date +%s)  # Update restart time
                fi
            fi
            sleep $SLEEP_INTERVAL
        fi

        if [ -f "$STOP_SIGNAL_FILE" ]; then
            log "Stop signal received. Terminating..."
            terminate_process
            rm -f "$STOP_SIGNAL_FILE"
            run=false
        fi
    done
}

# Trap signals for graceful shutdown
trap 'log "Script interrupted. Terminating processes..."; terminate_process; exit 0' SIGINT SIGTERM

# Run the main function
main