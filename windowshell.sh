run_window_main(){
    python main3.py &
    FUNNY_PID=$!

}

while true; do
    run_window_main
    sleep 3600
    kill $FUNNY_PID
done