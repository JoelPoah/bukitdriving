run_window_main(){
    python anya.py &
    ANYA_PID=$!

    #python joel.py &
    #JOEL_PID=$!
}

run=true

while $run; do
    # Get the current hour and minute
    current_hour=$(date +%H)
    current_minute=$(date +%M)
    
    # Calculate the current time in minutes since midnight
    current_time=$((10#$current_hour * 60 + 10#$current_minute))
    
    # Time boundaries in minutes since midnight
    start_time=$((2 * 60 + 20)) # 2:20 AM
    end_time=$((8 * 60 + 30))   # 8:30 AM
    
    # Check if the current time is outside the restricted window
    if (( current_time < start_time || current_time > end_time )); then
        run_window_main
    else
        echo "Current time is between 2:20 AM and 8:30 AM, waiting..."
        # Wait until the restricted period is over
        while (( current_time >= start_time && current_time <= end_time )); do
            sleep 60
            current_hour=$(date +%H)
            current_minute=$(date +%M)
            current_time=$((10#$current_hour * 60 + 10#$current_minute))
        done
        echo "breaking out of if time statement"
    fi
    
    # Generate a random number between 1200 and 1600 using Python
    random_sleep=$(python -c "import random; print(random.randint(1100, 1200))")
    
    for ((i=0; i<$random_sleep; i++)); do
        sleep 1
        if [ -f ./stop_signal.txt ]; then
            echo "Stop signal received, terminating..."
            kill $ANYA_PID
            #kill $JOEL_PID
            rm ./stop_signal.txt
            run=false
            break
        fi
    done

    if $run; then
        kill $ANYA_PID
        #kill $JOEL_PID
    fi
done
