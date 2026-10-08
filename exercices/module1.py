import requests
url1="https://api.open-meteo.com/v1/forecast"
url2="https://geo.api.gouv.fr/communes"
params1 = {"latitude": "abc", "longitude": -0.35, "current": "temperature_2m"}
params2 = {"nom": "Caen","codesPostaux": ["14000"], "fields": "population"}

def get_json(url, params):
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.url, response.text)
        return None
    
data1=get_json(url1, params1)
data2=get_json(url2, params2)

if data1:
    print("La température actuelle à Caen est de", data1["current"]["temperature_2m"], "°C.")
else:
    print("Impossible de récupérer les données météorologiques.")
if data2:
    print("La population de Caen est de", data2[0]["population"], "habitants.")
else:
    print("Impossible de récupérer les données de population.")
