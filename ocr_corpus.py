# --- Imports et client ---
import base64
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral   # <- même ligne d'import que dans test_ocr.py

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# --- Réglages ---
# CORPUS : où sont les PDF et le registre
# CACHE : où l'on enregistre le texte OCR, un fichier JSON par PDF
CORPUS = Path("corpus_assurance")
CACHE = Path("ocr_cache")
MODELE_OCR = "mistral-ocr-latest"   # alias : à figer avant la version finale


# --- OCR d'un PDF ---
# Envoie le PDF encodé en base64, comme pour ton test de ce matin,
# et renvoie une liste de pages : numéro dans le PDF (à partir de 1) + texte markdown
def ocr_pdf(chemin):
    with open(chemin, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
    reponse = client.ocr.process(
        model=MODELE_OCR,
        document={"type": "document_url",
                  "document_url": f"data:application/pdf;base64,{pdf_b64}"},
    )
    return [{"page_pdf": p.index + 1, "texte": p.markdown} for p in reponse.pages]


# --- Traitement d'un fichier, avec reprise et nouvelles tentatives ---
# Cache : si le résultat existe déjà, on saute le fichier.
# 429 : on attend 60 s et on réessaie, 3 fois au maximum ;
# toute autre erreur est relancée telle quelle pour qu'on la voie.
def traiter(chemin_relatif, nom_cache):
    sortie = CACHE / nom_cache
    if sortie.exists():
        print(f"déjà fait : {nom_cache}")
        return
    for tentative in range(1, 4):
        try:
            pages = ocr_pdf(CORPUS / chemin_relatif)
            break
        except Exception as e:
            if "429" not in str(e) or tentative == 3:
                raise
            print(f"429 sur {nom_cache}, tentative {tentative}/3, pause de 60 s")
            time.sleep(60)
    CACHE.mkdir(exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print(f"{nom_cache} : {len(pages)} pages")
    time.sleep(2)   # petite pause entre deux fichiers pour ne pas réveiller la limite


# --- Programme principal ---
# Lit le registre, puis traite les 3 PDF natifs et les 9 scans
if __name__ == "__main__":
    with open(CORPUS / "documents.json", encoding="utf-8") as f:
        registre = json.load(f)

    for doc in registre["documents"]:
        traiter(doc["fichier"], f"natif_{doc['assureur']}.json")

    for scan in registre["scans"]:
        traiter(scan["fichier"], Path(scan["fichier"]).stem + ".json")