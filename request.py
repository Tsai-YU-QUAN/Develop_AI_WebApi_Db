import requests

url = 'http://localhost:5000/predict_api'
r = requests.post(url, json={
                  'sepal_length': 5, 'sepal_width': 4, 'petal_length': 1, 'petal_width': 0})

print(r.json())
