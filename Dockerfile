# Dockerfile : la recette de l'image du RAG assurance (interface Streamlit).
# L'image contient le code et les bibliothèques, PAS la clé API ni l'index (texte des CG).
# Ces deux éléments sont fournis au lancement (voir la commande docker run dans le README).

# 1. Point de départ : un Linux minimal avec Python 3.14 déjà installé (même version que ton venv).
FROM python:3.14-slim

# 2. Dossier de travail dans le conteneur : toutes les commandes suivantes s'y exécutent.
WORKDIR /app

# 3. Les bibliothèques d'abord, seules : Docker garde cette étape en cache
#    tant que requirements.txt ne change pas, donc modifier le code ne réinstalle rien.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Le code, et seulement les 4 fichiers utiles (liste blanche : rien d'autre n'entre par erreur).
COPY app.py generate_assurance.py test_retrieval_assurance.py prompts.py ./

# 5. Documentation : l'app écoute sur le port 8501 dans le conteneur.
EXPOSE 8501

# 6. Commande lancée au démarrage du conteneur.
#    0.0.0.0 = accepter les connexions venant de l'extérieur du conteneur (sinon ton navigateur ne la voit pas).
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
