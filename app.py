import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURATION DE LA PAGE STREAMLIT
st.set_page_config(page_title="PMU PRO", layout="wide", initial_sidebar_state="collapsed")

# ------------------------------------------------------------------
# CONFIGURATION DES BLOCS HTML POUR LES PUBLICITÉS
# ------------------------------------------------------------------

# Code HTML pour la bannière du HAUT (Adsterra 728x90 / 320x50 automatique)
html_pub_haut = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; padding: 0; background-color: transparent; text-align: center; }
        .ad-container { display: flex; justify-content: center; align-items: center; width: 100%; min-height: 90px; }
    </style>
</head>
<body>
    <div class="ad-container">
        <script type="text/javascript">
            atOptions = {
                'key' : 'b9b40b1c4e412de03b6465589ab82662',
                'format' : 'iframe',
                'height' : 90,
                'width' : 728,
                'params' : {}
            };
        </script>
        <script type="text/javascript" src="https://www.highrevenueformat.com/b9b40b1c4e412de03b6465589ab82662/invoke.js"></script>
    </div>
</body>
</html>
"""

# Code HTML pour la bannière du BAS (CPM Network)
html_pub_bas = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; padding: 0; background-color: transparent; text-align: center; font-family: Arial, sans-serif; }
        .footer-ad { width: 100%; padding: 10px 0; }
        .label { font-size: 11px; color: #888; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="footer-ad">
        <div class="label">Sponsorisé</div>
        <div id="cpm-banner">
            <script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>
            <div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
        </div>
    </div>
</body>
</html>
"""

# ------------------------------------------------------------------
# EN-TÊTE DE L'APPLICATION ET PUBLICITÉ DU HAUT
# ------------------------------------------------------------------

# Insertion de la publicité Adsterra en haut
components.html(html_pub_haut, height=110, scrolling=False)

# Titre Principal
st.title("🏆 PMU PRO")
st.subheader("Analyse automatique et sélections")

# ------------------------------------------------------------------
# CONTENU PRINCIPAL (Ton espace de travail et algorithmes)
# ------------------------------------------------------------------
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("### 📊 Saisie des Données de Course")
    # Emplacement pour tes critères (Noms des chevaux, cotes, types de course)
    course_type = st.selectbox("Type de course :", ["Attelé", "Galop", "Haies", "Obstacle"])
    
    # Champ de texte persistant ou bouton pour lancer l'algorithme des 9 numéros
    if st.button("⚡ Générer la Sélection Stratégique"):
        st.success("Calcul effectué avec succès selon tes règles d'analyse !")
        # C'est ici que s'exécutera ton algorithme de tri automatique
        st.code("[Exemple] Numéros retenus : 3 - 7 - 4 - 9 - 12 - 14 - 5 - 1 - 16", language="text")

with col2:
    st.write("### 📌 Ma Sélection")
    # Zone d'affichage persistant pour la vérification des données enregistrées
    st.info("Les 9 numéros sélectionnés s'afficheront ici en continu pour vérification.")

# ------------------------------------------------------------------
# PIED DE PAGE ET PUBLICITÉ DU BAS
# ------------------------------------------------------------------
st.markdown("---")

# Insertion de la publicité CPM Network en bas
components.html(html_pub_bas, height=140, scrolling=False)
