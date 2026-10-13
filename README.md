## Ce que fait le projet
Ce projet permet aux locataires et aux bailleurs d'obtenir rapidement des réponses à des questions précises sur la location immobilière (préavis, restitution du dépôt de garantie, obligations du propriétaire, etc.), sans avoir à parcourir manuellement de nombreux documents.

Le système repose sur une architecture RAG (Retrieval-Augmented Generation) qui s'appuie sur un corpus de 30 documents issus du site officiel Service-Public.fr. À partir d'une question en langage naturel, il recherche les informations pertinentes dans cette base documentaire, puis génère une réponse contextualisée à l'aide d'un modèle de langage. Les réponses sont accompagnées de sources citées, permettant à l'utilisateur de vérifier les informations fournies.

Le système est conçu pour limiter les réponses non fondées : lorsqu'aucune information pertinente n'est trouvée dans le corpus, il doit indiquer qu'il ne dispose pas des éléments nécessaires pour répondre.

Ce projet d'apprentissage vise à comprendre et à expérimenter les mécanismes fondamentaux d'un RAG, de la recherche documentaire à la génération de réponses sourcées.

## Architecture

Le système fonctionne en deux phases : l'**indexation**, lancée une fois (ou quand le corpus change), et la **requête**, à chaque question.


flowchart LR
  subgraph Indexation [ingest.py — une fois]
    A[corpus_location/*.txt] --> B[Découpage 500 / 50]
    B --> C[Embeddings Mistral<br/>titre + texte]
    C --> D[(chunks.json<br/>vectors.npy)]
  end
  subgraph Requête [ask.py — à chaque question]
    Q[Question] --> E[Embedding]
    E --> F[Top 4 chunks<br/>cosinus]
    D --> F
    F --> G[Prompt : consigne + extraits + question]
    G --> H[mistral-small-latest]
    H --> R[Réponse + sources]
  end


| Fichier | Rôle | Entrée | Sortie |
|---|---|---|---|
| `doc_utils.py` | Lire et découper les documents (module utilitaire) | Dossier de `.txt` / un texte | Liste de `{source, texte}` / liste de chunks |
| `embed_utils.py` | Vectoriser des textes, mesurer leur proximité (module utilitaire) | Liste de textes / deux vecteurs | Liste de vecteurs / score cosinus |
| `ingest.py` | Construire l'index | `corpus_location/` | `chunks.json` + `vectors.npy` |
| `retrieve.py` | Trouver les k chunks les plus proches d'une question | Question + index | k paires (score, chunk) |
| `ask.py` | Répondre à une question avec sources | Question | Réponse sourcée ou refus |

### Lancer le projet



### Détail par fichier

## Fichier doc_utils.py
Contient deux fonctions qui permettent de lire les fichiers, de les découper en chunks qui serviront ensuite à alimenter le RAG #module utilitaire, importé par les autres scripts

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

    un RAG complet (ingestion, retrieval avec préfixe de titre, génération Mistral avec sources), deux diagnostics menés par tests (retrieval, puis génération), et une première évaluation sur 7 questions figées.

## Fichier embed_utils.py

Rôle : Génère des embeddings à partir de textes grâce à l’API Mistral, afin de les représenter sous forme de vecteurs numériques. Définit également une fonction de similarité cosinus permettant de mesurer la proximité entre deux vecteurs et donc d’évaluer la similarité sémantique entre des textes. #module utilitaire, importé par les autres scripts

Entrée :
textes : liste de textes à transformer en embeddings.
a, b : deux vecteurs numériques à comparer.

Sortie :
embed(textes) : liste de vecteurs numériques représentant les textes.
cosinus(a, b) : score de similarité compris entre -1 et 1, où une valeur proche de 1 indique une forte proximité entre les vecteurs.

## Fichier ingest.py
Rôle : Charge les documents du corpus, les découpe en segments (chunks) de 500 caractères avec un chevauchement de 50 caractères afin de conserver le contexte entre les segments. Associe à chaque chunk son titre et sa source, puis génère un embedding pour chaque segment à l’aide de l’API Mistral. Enfin, sauvegarde les chunks dans chunks.json et leurs vecteurs dans vectors.npy pour permettre leur utilisation lors de la recherche sémantique.

Entrée :
corpus_location : dossier contenant les documents à traiter.
size : taille maximale souhaitée des chunks (500 caractères).
overlap : nombre de caractères partagés entre deux chunks successifs (50 caractères).
L’API Mistral : utilisée pour générer les embeddings.

Sortie :
chunks.json : fichier contenant les chunks textuels, leur titre et leur document source.
vectors.npy : fichier contenant les embeddings associés aux chunks, utilisés pour calculer la similarité sémantique lors de la recherche.
Des informations affichées dans la console : nombre de documents chargés, nombre de vecteurs générés et dimension de chaque vecteur.

Gestion des erreurs : le programme s’arrête si le dossier est introuvable ou si aucun document n’a été chargé.


## Fichier retrieve.py

Rôle : Charge l’index documentaire constitué des chunks et de leurs embeddings, puis recherche les segments les plus pertinents par rapport à une question utilisateur. La question est transformée en embedding via l’API Mistral, puis comparée aux vecteurs des chunks à l’aide de la similarité cosinus. Les résultats sont ensuite triés par score décroissant afin de récupérer les k segments les plus proches sémantiquement.

Entrée :
chunks.json : fichier contenant les segments textuels, leurs titres et leurs sources.
vectors.npy : fichier contenant les embeddings associés aux chunks.
question : question posée par l’utilisateur, transmise en argument lors de l’exécution du script.
k : nombre de chunks les plus pertinents à récupérer (4 par défaut).

Sortie :
chunks, vectors : les segments documentaires et leurs vecteurs chargés en mémoire.
resultats : liste des k chunks les plus pertinents, chacun associé à son score de similarité cosinus, triée du score le plus élevé au plus faible.
Gestion des erreurs : le programme s’arrête si aucun argument n’est fourni ou si le nombre de chunks ne correspond pas au nombre de vecteurs de l’index.




## Fichier ask.py

Rôle : Permet à l’utilisateur de poser une question en langage naturel sur la location de logements et d’obtenir une réponse générée à partir du corpus documentaire. Le script récupère les chunks les plus pertinents grâce au module `retrieve`, assemble leurs contenus et leurs sources, puis transmet le contexte ainsi que la question à l’API Mistral, en utilisant le modèle `mistral-small-latest`. Un prompt système impose au modèle de s’appuyer uniquement sur les extraits fournis et de citer les sources entre crochets pour chaque affirmation. Si aucun extrait ne traite du sujet de la question, le modèle doit indiquer que l’information n’a pas été trouvée dans les documents.

Entrée :
 `question` : question de l’utilisateur, transmise en argument lors de l’exécution du script.
`chunks.json` et `vectors.npy` : fichiers contenant les segments documentaires et leurs embeddings, utilisés pour la recherche des extraits pertinents.
`MISTRAL_API_KEY` : clé d’accès à l’API Mistral, chargée depuis les variables d’environnement.
`mistral-small-latest` : modèle utilisé pour générer la réponse.

Sortie :
Les chunks récupérés, accompagnés de leur score de similarité cosinus et de leur source, affichés dans la console.
Une réponse en langage naturel générée par Mistral à partir des extraits sélectionnés, avec des références aux documents sources.
Un message de refus prédéfini si aucun extrait ne traite du sujet de la question.

Gestion des erreurs : le programme s’arrête si aucune question n’est fournie. Il dépend également de la disponibilité des fichiers d’index et de l’accès à l’API Mistral.

## Choix techniques

| Choix | Raison | Mesuré ? |
|---|---|---|
| Chunks de 500 caractères, overlap 50 | Valeur de départ du parcours, non comparée. Faiblesse connue : la coupe se fait au caractère, en plein mot ou en pleine liste (Q1 échoue pour cette raison). Piste : couper en fin de phrase ou par section. | Non — à mesurer au module 7 |
| k = 4 | Assez d'extraits pour répondre, sans ajouter de bruit ni de coût en tokens. | Non — à mesurer au module 7 |
| Préfixe du titre dans le texte vectorisé (`titre + ". " + texte`) | Le titre porte le sujet du document, absent des chunks du milieu. | Oui : chunk « Restitution » passé du rang 7 au rang 3 (0,841 → 0,855), sur une seule question — à confirmer au module 7 |
| `mistral-embed` | Cohérence de stack (un fournisseur, une clé), multilingue, aucun modèle à télécharger. | Non — choix par raisonnement |
| `mistral-small-latest` | Peu coûteux pour les premiers essais. | Non — essai avec un modèle plus gros prévu au module 7 |
| Consigne système stricte, puis assouplie | Avec la consigne stricte, le modèle refusait alors que les bons extraits étaient fournis. Assouplie : utiliser les extraits même formulés autrement, refuser seulement si aucun ne traite du sujet. | Oui : série 1 (stricte) 0/5 juste, 4 refus à tort ; série 2 (assouplie) 1 juste, 2 partielles, 2 fausses ; refus corrects maintenus (2/2) |
| Index en `json` + `npy`, cosinus avec `numpy` | 148 chunks : recherche exhaustive instantanée, aucune dépendance, calcul visible. | Non — migration vers Chroma au module 7 |

## Limites connues

- **Découpage au caractère** : les chunks coupent en plein mot ou en pleine liste, ce qui fait échouer des questions dont la réponse est pourtant dans le bon fichier (Q1, Q2).
- **Pas de seuil de pertinence** : le retrieval renvoie toujours k chunks, même quand la question est hors sujet (les scores restent élevés, autour de 0,8, avec des embeddings en français). Le refus repose entièrement sur la consigne du modèle.
- **Évaluation limitée** : 7 questions, notées à la main. Les résultats sont indicatifs, pas statistiques.
- **Erreurs non gérées** : index absent ou API Mistral indisponible font planter `ask.py` avec un traceback.
- **Pas de mémoire de conversation** : chaque question est traitée seule, sans tenir compte des précédentes.
- **Corpus** : 30 fiches rédigées à partir de Service-Public.fr à une date donnée ; une évolution de la loi n'est pas reflétée sans mise à jour et réindexation complète.

## Prochaines étapes

1. **Évaluation chiffrée** : 15 questions figées dans `eval.json` (dont 3 sans réponse), `evaluate.py` qui calcule le hit rate, réponses notées juste / partielle / fausse / refus correct.
2. **Essais une variable à la fois** : découpage par phrase ou par section, taille des chunks, k, préfixe du titre, modèle de génération — chaque essai consigné dans un tableau.
3. **Base vectorielle** : migration de l'index vers Chroma.
4. **Au-delà** : ingestion de PDF, interface minimale pour un utilisateur non technique.

## Parcours d'apprentissage

Ce RAG est l'aboutissement d'un parcours en modules. Etapes précédentes : appels d'API avec `requests` et gestion des erreurs, manipulation de JSON, lecture et découpage de fichiers, appels à un LLM (résumé de document en JSON, conversation multi-tours, calcul du coût en tokens), embeddings et recherche sémantique.