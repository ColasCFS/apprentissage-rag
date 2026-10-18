# --- Imports et réglages ---
# difflib : module standard de Python qui mesure la ressemblance entre deux textes
# re : expressions régulières, ici pour uniformiser les espaces
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

CORPUS = Path("corpus_assurance")
CACHE = Path("ocr_cache")


# --- Normalisation ---
# Minuscules, et toute suite d'espaces ou de retours à la ligne remplacée par un seul espace :
# deux pages identiques ne doivent pas sembler différentes à cause de la mise en forme
def normaliser(texte):
    return re.sub(r"\s+", " ", texte.lower()).strip()


# --- Programme principal ---
# Pour chaque scan : score de ressemblance (de 0 à 1) avec chaque page native
# du même assureur, puis affichage des deux meilleures pages
if __name__ == "__main__":
    with open(CORPUS / "documents.json", encoding="utf-8") as f:
        registre = json.load(f)

    for scan in registre["scans"]:
        nom = Path(scan["fichier"]).stem
        with open(CACHE / f"{nom}.json", encoding="utf-8") as f:
            texte_scan = normaliser(json.load(f)[0]["texte"])
        with open(CACHE / f"natif_{scan['assureur']}.json", encoding="utf-8") as f:
            pages_natives = json.load(f)

        scores = []
        for page in pages_natives:
            ratio = SequenceMatcher(None, texte_scan, normaliser(page["texte"])).ratio()
            scores.append((ratio, page["page_pdf"]))
        scores.sort(reverse=True)

        (s1, p1), (s2, p2) = scores[0], scores[1]
        print(f"{nom} | déclarée {scan['page_declaree']} | "
              f"meilleure : page PDF {p1} ({s1:.2f}) | 2e : page PDF {p2} ({s2:.2f})")