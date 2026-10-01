import json

client= {"nom":"Legrand","siren":"123456789","contrats":[{"numero":"11","type":"RC Pro","montant_annuel":100},{"numero":"12","type":"RC Entreprise","montant_annuel":200},{"numero":"13","type":"Flotte Auto","montant_annuel":300}]}
print(json.dumps(client, ensure_ascii=False, indent=2))

with open("client.json", "w", encoding="utf-8") as f:
    json.dump(client, f, ensure_ascii=False, indent=2)

print(len(client))
print(len(client["contrats"]))
print(len(client["contrats"][1]["type"]))
print(client["Siren"])
