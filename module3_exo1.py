from pathlib import Path

def charger_documents(dossier):
    dossier = Path(dossier)
    documents = list()
    if not dossier.exists():
            raise FileNotFoundError(f"Le dossier {dossier} n'existe pas.")
    for fichier in dossier.glob("*.txt"):
        with open(fichier, "r", encoding="utf-8") as f:
            texte = f.read()
        documents.append({"source": fichier.name, "texte": texte})
    return documents


try:
    documents = charger_documents("docs")
    print(len(documents[0]))
    print(len(documents[0]["texte"]))
except FileNotFoundError as e:
    print(e)
    raise SystemExit(1)
print(f"Nombre de documents chargés : {len(documents)}")
print("suite")
    
