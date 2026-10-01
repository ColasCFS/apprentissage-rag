import json
import requests

url1="https://data.geopf.fr/geocodage/search"

params1 = {"q": "1 place de la Concorde Paris", "limit": 1}

def get_json(url, params):
    response = requests.get(url, params=params, timeout=10)
    print(response.url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

data1=get_json(url1, params1)

print(type(data1))
print(data1.keys())
print(data1["features"][0])
print("La longitude est:", data1["features"][0]["geometry"]["coordinates"][0])
print("La latitude est:", data1["features"][0]["geometry"]["coordinates"][1])
print("Le code postale est ",data1["features"][0]["properties"]["postcode"])