import requests
import json
url1="https://recherche-entreprises.api.gouv.fr/search"

params1 = {"q": "Soule" }

def get_json(url, params):
    response = requests.get(url, params=params, timeout=10)
    print(response.url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None
    
data1=get_json(url1, params1)
if data1 is None: exit()

resultat = []
for enterprise in data1["results"]:
    
    nom = enterprise.get("nom_complet")
    siren = enterprise.get("siren")
    siege = enterprise.get("siege") or {}
    nom_commune = siege.get("libelle_commune")
    departement = siege.get("departement")
    ligne = {"nom": nom, "siren": siren, "nom_commune": nom_commune, "departement": departement}
    resultat.append(ligne)

print(len(resultat))

resultat_31= []
for d in resultat:
    if d.get("departement") == "31":
        resultat_31.append(d)

resultat_31_bis=[d for d in resultat if d.get("departement") == "31"]
print(resultat_31_bis)

print(resultat_31_bis == resultat_31)

with open("entreprises.json", "w", encoding="utf-8") as f:
    json.dump(resultat_31, f, ensure_ascii=False, indent=2)