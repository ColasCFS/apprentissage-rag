from pathlib import Path

size = 10
overlap = 3


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


def chunk_text(text, size, overlap):
    if size <= overlap or overlap < 0:
        raise ValueError(
            f"La taille du chunk size={size} doit être supérieure à l'overlap overlap={overlap} "
            "et l'overlap supérieur ou égal à 0."
        )
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunk = text[i:i + size]
        if i == 0 or i + overlap < len(text):
            chunks.append(chunk)
    return chunks


if __name__ == "__main__":
    try:
        documents = charger_documents("docs")
    except FileNotFoundError as e:
        print(e)
        raise SystemExit(1)

    print(f"Nombre de documents chargés : {len(documents)}")
    print("suite")

    chunks = chunk_text(documents[0]["texte"], size, overlap)
    print(len(chunks))

    print(chunk_text("abc", 5, 3))
    print(chunk_text("abcdefghijkl", 5, 2))
    print(chunk_text("abcdefgh", 5, 2))
    print(chunk_text("ab", 5, 3))
    print(chunk_text(charger_documents("docs")[0]["texte"], size, overlap))

