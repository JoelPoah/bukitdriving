run_window_main(){
    python main2.py &
    FUNNY_PID=$!

}

while true; do
    run_window_main
    sleep 21600
    kill $FUNNY_PID
done