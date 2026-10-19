# app.py
# Rôle : interface web du RAG assurance, pour un utilisateur qui ne code pas.
# Entrée : une question tapée + les assureurs cochés dans la barre latérale.
# Sortie : la réponse du modèle, puis les extraits utilisés (assureur, page, natif ou scan, score, texte).
# Lancement : streamlit run app.py  (ouvre http://localhost:8501 dans le navigateur)
# Ce qui peut casser en silence :
#   - Streamlit relance tout ce fichier à chaque clic ; l'index n'est chargé qu'une fois
#     parce que Python ne réimporte pas un module déjà importé ;
#   - aucun assureur coché = recherche sur tout le corpus (comportement de l'évaluation).

# --- Bloc 1 : imports ---
# Toute la logique vient de generate_assurance.py : l'interface ne refait ni la recherche
# ni l'appel au modèle (séparation interface / logique, section 12.2 du cours).
import streamlit as st
from generate_assurance import repondre, K

ASSUREURS = ["MAIF", "MMA", "AXA"]

# --- Bloc 2 : en-tête de la page ---
st.set_page_config(page_title="Assistant CG habitation", page_icon="🏠")
st.title("Assistant conditions générales — assurance habitation")
st.caption("Prototype de démonstration. Les réponses doivent être vérifiées dans les extraits cités : "
           "elles ne remplacent ni les conditions particulières ni l'avis d'un conseiller.")

# --- Bloc 3 : barre latérale, choix des assureurs ---
# Cocher deux ou trois assureurs garantit que chacun a sa part des extraits (8 → 4 + 4 ou 3 + 3 + 2).
st.sidebar.header("Assureurs à interroger")
choisis = [a for a in ASSUREURS if st.sidebar.checkbox(a, value=False)]
if choisis:
    st.sidebar.write(f"{K} extraits répartis entre : {', '.join(choisis)}")
else:
    st.sidebar.write(f"Aucun coché : recherche sur tout le corpus ({K} extraits).")
st.sidebar.info("CG AXA : édition avril 2009, antérieure à la loi Hamon — document volontairement périmé.")

# --- Bloc 4 : la question ---
question = st.text_area("Votre question", placeholder="Ex. : Quelle franchise la MAIF applique-t-elle en cas de vol de bijoux ?")
lancer = st.button("Répondre")

# --- Bloc 5 : réponse et sources ---
# On ne lance l'appel (payant, quelques secondes) que sur clic et avec une vraie question.
if lancer and question.strip():
    with st.spinner("Recherche dans les conditions générales…"):
        try:
            reponse, extraits, tokens = repondre(question.strip(), assureurs=choisis or None)
        except Exception as e:
            st.error(f"L'appel a échoué : {e}")
            st.stop()

    st.subheader("Réponse")
    st.markdown(reponse)

    st.subheader("Extraits utilisés")
    st.table([
        {"Rang": e["rang"], "Assureur": e["assureur"], "Page PDF": e["page_pdf"],
         "Origine": e["origine"], "Score": e["score"]}
        for e in extraits
    ])
    for e in extraits:
        with st.expander(f"{e['rang']}. {e['assureur']} p.{e['page_pdf']} ({e['origine']})"):
            st.write(e["texte"])

    st.caption(f"Tokens : {tokens['entree']} en entrée, {tokens['sortie']} en sortie.")
elif lancer:
    st.warning("Écrivez d'abord une question.")
