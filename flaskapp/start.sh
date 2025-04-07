echo start server
waitress-serve --call 'wsgi:create_app' & APP_PID=$!
echo $APP_PID
sleep 5
echo "Start test"
python3 test.py
sleep 5
kill -TERM $APP_PID
echo "End test"
exit 0