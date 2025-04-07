import requests

r = requests.get('http://localhost:8080/trans')

print(r.status_code)
