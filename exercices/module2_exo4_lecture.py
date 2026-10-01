import requests
import json

with open("entreprises.json", "r", encoding="utf-8") as f:
    data = json.load(f)
print(type(data))
print(len(data))

