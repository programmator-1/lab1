echo start server
gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
echo $APP_PID
sleep 5
echo start client
python3 tests.py
kill -TERM $APP_PID
echo process gunicorn kills
exit 0