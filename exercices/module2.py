import json
import requests

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
    
def extraire_entreprises(data):
    resultat = []
    for entreprises in data["results"]:
        nom = entreprises.get("nom_complet")
        siren = entreprises.get("siren")
        siege = entreprises.get("siege") or {}
        nom_commune = siege.get("libelle_commune")
        departement = siege.get("departement")
        ligne = {"nom": nom, "siren": siren, "nom_commune": nom_commune, "departement": departement}
        resultat.append(ligne)
    return resultat

def sauvegarder_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data1=get_json(url1, params1)
if data1 is None: exit()

entreprises = extraire_entreprises(data1)
print(len(entreprises))
sauvegarder_json(entreprises, "entreprises.json")