from exercices.api_utils import get_json

url1 = "https://api.open-meteo.com/v1/forecast"
params1 = {"latitude": 49.18, "longitude": -0.35, "current": "temperature_2m"}

data1 = get_json(url1, params1)
print(data1)