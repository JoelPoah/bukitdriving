run_window_main() {

    python ryan.py &
    RYAN_PID=$!

    # python joel.py &
    # JOEL_PID=$!

}

run=true

while $run; do
    # Get the current hour and minute
    current_hour=$(date +%H)
    current_minute=$(date +%M)
    
    # Calculate the current time in minutes since midnigh
    current_time=$((10#$current_hour * 60 + 10#$current_minute))
    
    # Define restricted time windows in minutes since midnight
    restricted_times=(
        $((2 * 60 + 30))  $((3 * 60 + 30))  # 2:30 AM - 3:30 AM
        $((7 * 60 + 31))      $((11 * 60))      # 7:31 AM - 11:00 AM
        $((18 * 60))      $((19 * 60))      # 6:00 PM - 7:00 PM
    )

    in_restricted=false
    for ((i = 0; i < ${#restricted_times[@]}; i += 2)); do
        start_time=${restricted_times[i]}
        end_time=${restricted_times[i + 1]}
        if (( current_time >= start_time && current_time < end_time )); then
            in_restricted=true
            break
        fi
    done
    
    if ! $in_restricted; then
        run_window_main
    else
        echo "Current time is in a restricted window, waiting..."
        sleep 60
        continue
    fi
    
    # Generate a random sleep time between 1100 and 1200 seconds
    random_sleep=$(python -c "import random; print(random.randint(1200, 1600))")

    for ((i = 0; i < random_sleep; i++)); do
        sleep 1
        if [ -f ./stop_signal.txt ]; then
            echo "Stop signal received, terminating..."


            kill -TERM $RYAN_PID
            wait $RYAN_PID
            pkill -TERM -P $RYAN_PID

            kill -TERM $STEPHY_PID
            wait $STEPHY_PID
            pkill -TERM -P $STEPHY_PID

            # kill -TERM $CHINA_PID
            # wait $CHINA_PID
            # pkill -TERM -P $CHINA_PID

            #kill -TERM $JOEL_PID
            #wait $JOEL_PID
            #pkill -TERM -P $JOEL_PID

            # kill -TERM $ASHWARY_PID
            # wait $ASHWARY_PID
            # pkill -TERM -P $ASHWARY_PID

            sleep 10
            rm ./stop_signal.txt
            run=false
            break
        fi
    done

    if $run; then
        # kill -TERM $ASHWARY_PID
        # wait $ASHWARY_PID
        # pkill -TERM -P $ASHWARY_PID

        kill -TERM $RYAN_PID
        wait $RYAN_PID
        pkill -TERM -P $RYAN_PID

        # kill -TERM $CHINA_PID
        # wait $CHINA_PID
        # pkill -TERM -P $CHINA_PID

        #kill -TERM $JOEL_PID
        #wait $JOEL_PID
        #pkill -TERM -P $JOEL_PID


        kill -TERM $STEPHY_PID
        wait $STEPHY_PID
        pkill -TERM -P $STEPHY_PID

        sleep 10

    fi
done
