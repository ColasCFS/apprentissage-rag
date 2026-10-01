import requests
url1="https://jsonplaceholder.typicode.com/posts"
Dict={"Nom":"Legrand","Prénom":"Nicolas","Age":30,"Ville":"Caen"}
response = requests.post(url1, json=Dict)
print(response.status_code)
data_reponse = response.json()
print(data_reponse)
for cle in Dict:
    print(cle, ":", Dict[cle] == data_reponse[cle])