#!/bin/bash

# Function to run the Python bot script
run_window_main(){
    python bot.py &
    JOEL=$!
}

# Infinite loop to run the function every hour (3600 seconds)
while true; do
    run_window_main
    sleep 3600
    kill $JOEL
done
