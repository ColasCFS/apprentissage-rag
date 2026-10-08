from retrieve import load_index
from embed_utils import embed
from embed_utils import cosinus

chunk, vectors=load_index()

texte_recherche = "Le délai court à partir de la remise des clés"

resultats = [element for element in chunk if texte_recherche in element["texte"]]
question= "Combien de temps le propriétaire a-t-il pour rendre le dépôt de garantie ?"
titre = "Dépôt de garantie"

brut = resultats[0]["texte"]
compo = titre + ". " + brut          

vecs = embed([question, brut, compo])        

print(f"Brut   : {cosinus(vecs[0], vecs[1]):.3f}")
print(f"Préfixe: {cosinus(vecs[0], vecs[2]):.3f}")

i = chunk.index(resultats[0])
print(f"Position : {i}")
print(f"Stocké vs recalculé : {cosinus(vecs[1], vectors[i]):.5f}")

