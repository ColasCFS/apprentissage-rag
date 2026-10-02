## Architecture : les deux briques du module 3

### charger_documents(dossier)
- **Rôle** : lire les fichiers `.txt` d'un dossier et les mettre en mémoire, sous une forme que le découpage peut utiliser. Elle lit seulement, elle ne modifie rien sur le disque.
- **Entrée** : un nom de dossier (texte, ex. `"docs"`). Elle cherche elle-même les fichiers avec `glob("*.txt")`, donc les autres formats (`.md`, `.pdf`) sont ignorés.
- **Sortie** : une liste de dicts, un par fichier, avec les clés `"source"` (nom du fichier) et `"texte"` (son contenu).
- **Ce qui peut casser sans bruit** : un dossier qui existe mais ne contient aucun `.txt` renvoie `[]` sans erreur. Protection : dans `main.py`, le garde « aucun chunk » arrête le programme avec un message clair. Un dossier inexistant, lui, lève une `FileNotFoundError`, donc ce n'est pas silencieux.

### chunk_text(text, size, overlap)
- **Rôle** : découper un texte en morceaux plus petits, qui serviront ensuite dans le RAG.
- **Entrée** : un seul texte à la fois (`str`), une taille de chunk (entier) et un chevauchement (entier).
- **Sortie** : la liste des chunks de ce texte. Chaque chunk fait au plus `size` caractères, seul le dernier peut être plus court. La liste unique de tous les chunks est construite par `main.py`, avec `extend`.
- **Ce qui peut casser sans bruit** : la fonction coupe aux positions, sans regarder les mots, donc un chunk peut commencer ou finir au milieu d'un mot (`'re le mont' suivi de 'ontant du '`), ce qui le rend peu exploitable. Ce cas n'est pas encore protégé. Les autres risques le sont : `overlap` invalide par une `ValueError`, chunk de fin redondant par la règle `i == 0 or i + overlap < len(text)`, texte vide par le `continue` de `main.py`.