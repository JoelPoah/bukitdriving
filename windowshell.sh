run_window_main(){
    python main2.py &
    FUNNY_PID=$!

}

while true; do
    run_window_main
    sleep 1200
    kill $FUNNY_PID
done