import requests
url1="https://api.open-meteo.com/v1/forecast"
url2="https://geo.api.gouv.fr/communes"
params1 = {"latitude": 49.18, "longitude": -0.35, "current": "temperature_2m"}
params2 = {"nom": "Caen", "fields": "population"}
response1 = requests.get(url1, params=params1, timeout=10)
response2 = requests.get(url2, params=params2, timeout=10)
print(response1.status_code)
print(response2.status_code)
print(response1.url)
print(response2.url)
data1=response1.json()
data2=response2.json()
print("La température à Caen est de " + str(data1["current"]["temperature_2m"]) + "°C")
print("La population de Caen est de " + str(data2[0]["population"]) + " habitants.")