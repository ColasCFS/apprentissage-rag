# --- Imports et réglages ---
import json
import re
from pathlib import Path
from doc_utils import chunk_text   # ton chunker du module 3

CORPUS = Path("corpus_assurance")
CACHE = Path("ocr_cache")
TAILLE_MAX = 500     # au-delà, un paragraphe est recoupé (sauf les tableaux)
TAILLE_MIN = 30      # en dessous, un bloc est jeté (numéro de page, en-tête isolé)
IMAGE = re.compile(r"!\[.*?\]\(.*?\)")   # balises d'image du markdown OCR : ![img-0.jpeg](img-0.jpeg)
TAILLE_TABLEAU = 1500   # au-delà, un tableau est découpé par groupes de lignes


# --- Assemblage des pages : natives, sauf quand un scan les remplace ---
# Clé (assureur, page_pdf) : c'est la page PDF vérifiée qui relie un scan à sa page native
def pages_du_corpus(registre):
    scans = {(s["assureur"], s["page_pdf"]): s for s in registre["scans"]}
    pages = []
    for doc in registre["documents"]:
        with open(CACHE / f"natif_{doc['assureur']}.json", encoding="utf-8") as f:
            natives = json.load(f)
        for p in natives:
            cle = (doc["assureur"], p["page_pdf"])
            if cle in scans:
                scan = scans[cle]
                with open(CACHE / f"{Path(scan['fichier']).stem}.json", encoding="utf-8") as f:
                    texte = json.load(f)[0]["texte"]
                origine, page_imprimee = "scan", scan["page_imprimee"]
            else:
                texte, origine, page_imprimee = p["texte"], "natif", None
            pages.append({
                "assureur": doc["assureur"], "reference": doc["reference"],
                "date_version": doc["date_version"], "page_pdf": p["page_pdf"],
                "page_imprimee": page_imprimee, "origine": origine, "texte": texte,
            })
    return pages


# --- Création d'un chunk ---
# Texte vectorisé : assureur + texte pour un paragraphe ;
# assureur + titre + texte pour un morceau de tableau, dont l'en-tête seul
# ne dit pas de quoi parle le tableau. Le titre reste en métadonnée partout.
def creer_chunk(page, titre, texte):
    chunk = {k: v for k, v in page.items() if k != "texte"}
    chunk["titre"] = titre
    chunk["texte"] = texte
    if texte.startswith("|"):
        chunk["texte_vectorise"] = f"{page['assureur']} | {titre}\n{texte}"
    else:
        chunk["texte_vectorise"] = f"{page['assureur']}\n{texte}"
    return chunk


# --- Découpage d'un tableau markdown (point C) ---
# Les 2 premières lignes sont l'en-tête et la ligne de séparation |---|.
# On remplit des groupes de lignes jusqu'à TAILLE_TABLEAU, en répétant l'en-tête
# dans chaque groupe : chaque morceau reste un tableau lisible avec ses colonnes.
def decouper_tableau(bloc):
    lignes = bloc.split("\n")
    entete, corps = lignes[:2], lignes[2:]
    morceaux, groupe = [], []
    for ligne in corps:
        if groupe and len("\n".join(entete + groupe + [ligne])) > TAILLE_TABLEAU:
            morceaux.append("\n".join(entete + groupe))
            groupe = []
        groupe.append(ligne)
    if groupe:
        morceaux.append("\n".join(entete + groupe))
    return morceaux


# --- Découpage d'une page (point B : regroupement des petits paragraphes) ---
# Les paragraphes courts consécutifs s'accumulent dans un tampon jusqu'à TAILLE_MAX.
# Le tampon est vidé (transformé en chunk) quand : il serait trop plein,
# un titre change de section, un tableau ou un long paragraphe arrive, la page finit.
# On ne fusionne jamais entre deux pages : la page citée doit rester exacte.
def decouper_page(page, titre):
    chunks, tampon = [], ""
    texte = IMAGE.sub("", page["texte"])
    for bloc in texte.split("\n\n"):
        bloc = bloc.strip()
        if bloc.startswith("#"):
            if tampon:
                chunks.append(creer_chunk(page, titre, tampon))
                tampon = ""
            premiere_ligne, _, reste = bloc.partition("\n")
            titre = premiere_ligne.lstrip("#").strip().strip("*").strip()
            bloc = reste.strip()
        if len(bloc) < TAILLE_MIN:
            continue
        # Tableau ou long paragraphe : on vide le tampon, puis on découpe à part
        if bloc.startswith("|") or len(bloc) > TAILLE_MAX:
            if tampon:
                chunks.append(creer_chunk(page, titre, tampon))
                tampon = ""
            if bloc.startswith("|"):
                morceaux = decouper_tableau(bloc) if len(bloc) > TAILLE_TABLEAU else [bloc]
            else:
                morceaux = chunk_text(bloc, TAILLE_MAX, 50)
            for m in morceaux:
                chunks.append(creer_chunk(page, titre, m))
            continue
        # Paragraphe court : on l'ajoute au tampon, en le vidant d'abord s'il déborderait
        if tampon and len(tampon) + 2 + len(bloc) > TAILLE_MAX:
            chunks.append(creer_chunk(page, titre, tampon))
            tampon = ""
        tampon = f"{tampon}\n\n{bloc}" if tampon else bloc
    if tampon:
        chunks.append(creer_chunk(page, titre, tampon))
    return chunks, titre


# --- Programme principal : assemblage, découpage, sauvegarde, statistiques ---
if __name__ == "__main__":
    with open(CORPUS / "documents.json", encoding="utf-8") as f:
        registre = json.load(f)

    pages = pages_du_corpus(registre)
    chunks, titre, assureur_precedent = [], "", None
    for page in pages:
        if page["assureur"] != assureur_precedent:   # nouveau document : on oublie le titre
            titre, assureur_precedent = "", page["assureur"]
        nouveaux, titre = decouper_page(page, titre)
        chunks.extend(nouveaux)

    with open("chunks_assurance.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    # Contrôles : volumes, origine, tableaux, taille maximale, un exemple de chunk scanné
    print(f"Pages : {len(pages)} (dont {sum(p['origine'] == 'scan' for p in pages)} scannées)")
    print(f"Chunks : {len(chunks)}")
    for a in ["MAIF", "MMA", "AXA"]:
        print(f"  {a} : {sum(c['assureur'] == a for c in chunks)}")
    print(f"Chunks issus de scans : {sum(c['origine'] == 'scan' for c in chunks)}")
    print(f"Tableaux : {sum(c['texte'].startswith('|') for c in chunks)}")
    print(f"Plus long chunk : {max(len(c['texte']) for c in chunks)} caractères")
    exemple = next(c for c in chunks if c["origine"] == "scan" and c["assureur"] == "MAIF")
    print("\nExemple :\n" + exemple["texte_vectorise"][:400])