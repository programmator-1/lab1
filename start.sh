echo start server
gunicorn --bind 127.0.0.1:8080 myapp:app & APP_PID=$!
echo $APP_PID
sleep 5
echo "Start test"
python3 test.py
sleep 5
kill -TERM $APP_PID
echo "End test"
exit 0