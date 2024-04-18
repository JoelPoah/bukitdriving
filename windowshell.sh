run_window_main(){
    python main.py &
    FUNNY_PID=$!

}

while true; do
    run_window_main
    sleep 600
    kill $FUNNY_PID
done