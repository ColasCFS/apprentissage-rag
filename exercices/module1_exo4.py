import requests
url1="https://recherche-entreprises.api.gouv.fr/search"
Nomcherche="Nicolas"
params1 = {"q": Nomcherche, "code_postal": "75010"}

def get_json(url, params):
    response = requests.get(url, params=params, timeout=10)
    print(response.url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None
    
data1=get_json(url1, params1)
print(data1["results"][0]["siege"]["libelle_commune"])
for entreprise in data1["results"][:5]:
    print(entreprise["nom_complet"], "-", entreprise["siege"]["libelle_commune"],"-",entreprise["nombre_etablissements_ouverts"])
