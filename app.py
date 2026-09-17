import streamlit as st
import math
import pandas as pd
import altair as alt
import os

# --- GESTION DU COMPTEUR DE VISITEURS PERSISTANT (PUBLIC) ---
def gerer_compteur():
    fichier_compteur = "visiteurs.txt"
    if not os.path.exists(fichier_compteur):
        with open(fichier_compteur, "w") as f:
            f.write("0")
    with open(fichier_compteur, "r") as f:
        try:
            visiteurs = int(f.read().strip())
        except ValueError:
            visiteurs = 0
    if 'visite_enregistree' not in st.session_state:
        visiteurs += 1
        with open(fichier_compteur, "w") as f:
            f.write(str(visiteurs))
        st.session_state['visite_enregistree'] = True
    return visiteurs

total_visiteurs = gerer_compteur()

# 1. CONFIGURATION DE LA PAGE & VISUELS PRO
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

st.markdown("""<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}
.pub-banner {background-color: #fef08a; border: 2px dashed #ca8a04; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; color: #854d0e; font-weight: bold;}
.pub-sidebar {background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; text-align: center; border-radius: 6px; margin-top: 20px; color: #1e40af;}
</style>""", unsafe_allow_html=True)

# 2. SYSTÈME DE DOUBLE CLÉ SÉCURISÉ (ADMIN / USER)
MOT_DE_PASSE_USER = "PMU_PRO_2026"
MOT_DE_PASSE_ADMIN = "ADMIN7670" # Votre seconde clé maîtresse

if 'authentifie' not in st.session_state:
    st.session_state.authentifie = False
if 'est_admin' not in st.session_state:
    st.session_state.est_admin = False

def verifier_mot_de_passe():
    saisie = st.session_state["mot_de_passe_saisi"]
    if saisie == MOT_DE_PASSE_ADMIN:
        st.session_state.authentifie = True
        st.session_state.est_admin = True
    elif saisie == MOT_DE_PASSE_USER:
        st.session_state.authentifie = True
        st.session_state.est_admin = False
    else:
        st.error("❌ Clé d'accès incorrecte.")

if not st.session_state.authentifie:
    st.title("🔒 Accès Restreint - Plateforme PMU Pro")
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

# 3. INITIALISATION DURABLE DU NOMBRE DE PARTANTS
if 'mises' not in st.session_state:
    st.session_state.mises = {f"N°{i}": float(10000 - (i*500)) for i in range(1, 17)}

# 4. BARRE LATÉRALE - ESPACE AUTEUR & PUBLICITÉS DYNAMIQUES
st.sidebar.header("📚 Espace Auteur & Pro")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")

st.sidebar.markdown("---")

# Les textes de publicités par défaut
texte_banner_defaut = "📢 ESPACE PUBLICITAIRE DISPONIBLE - Louez cet encart pour booster votre visibilité !"
texte_sidebar_defaut = "Formations certifiées en électricité."

# Si admin connecté, il peut modifier les pubs, sinon affichage standard
if st.session_state.est_admin:
    st.sidebar.header("📢 Administration des Publicités")
    texte_pub_principal = st.sidebar.text_area("Bannière du haut :", value=texte_banner_defaut)
    texte_pub_sidebar = st.sidebar.text_input("Texte pub latérale :", value=texte_sidebar_defaut)
else:
    texte_pub_principal = texte_banner_defaut
    texte_pub_sidebar = texte_sidebar_defaut

st.markdown(f"""<div class="pub-banner">{texte_pub_principal}</div>""", unsafe_allow_html=True)
st.sidebar.markdown(f"""<div class="pub-sidebar">🎯 <b>PARTENAIRE</b><br><small>{texte_pub_sidebar}</small></div>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique")
type_course = st.sidebar.selectbox("Spécialité de la course :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.session_state.est_admin = False
    st.rerun()

# BOUTON WHATSAPP & BLOC CONTACT (VISIBLE PAR TOUS)
st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact & Support")
st.sidebar.write("Une question ou une demande de publicité ?")
lien_whatsapp = "https://wa.me"
st.sidebar.markdown(f'<a href="{lien_whatsapp}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold;">🟢 Nous contacter sur WhatsApp</button></a>', unsafe_allow_html=True)
st.sidebar.write("📧 **Email :** jb.aime23@gmail.com")


# 5. MOTEURS DE CALCUL MATHÉMATIQUES & PROBABILITÉS
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cotes[cheval] = max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10)
        else: cotes[cheval] = 99.0
    return cotes, masse_totale

def calculer_paris_complexes(mises, taux_comb):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0: return {}
    masse_net = masse_totale * (1 - taux_comb)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    c_couples = {}
    chevaux = list(mises.keys())[:8]
    
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p_comb = (probabilites[c1]*probabilites[c2]) * 2
            if p_comb > 0: 
                c_couples[f"{c1} - {c2}"] = max(math.floor((masse_net / (masse_net * p_comb * 0.4)) * 100) / 100, 2.0)
    return c_couples

def analyse_ia_avec_regles_expert(mises, specialite):
    scores_base = {f"N°{i}": 50 + (i % 3)*12 for i in range(1, 17)}
    analyses = {}
    
    for i in range(1, 17):
        cheval_key = f"N°{i}"
        if 1 <= i <= 4:
            analyses[cheval_key] = "Zone Favoris (Règle Expert : 1 à 2 numéros sortent souvent ici)."
            scores_base[cheval_key] += 10
        elif i == 5 or i == 4:
            analyses[cheval_key] = "Point d'appui intermédiaire (Règle Expert : Présence fréquente d'un numéro)."
            scores_base[cheval_key] += 8
        elif 6 <= i <= 12:
            analyses[cheval_key] = "Alerte Outsiders Spéculatifs (Règle Expert : Zone à forte récurrence, 1 ou 2 numéros ici)."
            scores_base[cheval_key] += 15
        elif 13 <= i <= 16:
            analyses[cheval_key] = "Zone Grosses Cotes / Tocard ciblé (Règle Expert : 1 numéro à chercher ici pour casser les rapports)."
            scores_base[cheval_key] += 5
            
        if specialite == "Attelé (Trot)" and (6 <= i <= 12 or 1 <= i <= 4):
            analyses[cheval_key] += " Modèle Attelé renforcé (+ de régularité détectée)."
            scores_base[cheval_key] += 7
            
    return scores_base, analyses

# 6. ENSEMBLE DES ONGLETS D'AFFICHAGE
st.title("🏇 PMU Pro Suite Ultimate Hub v4.5")

# Affichage du compteur public de visiteurs visible par tous
st.info(f"👥 **Nombre total de visiteurs sur la plateforme : {total_visiteurs}**")

onglet1, onglet2, onglet3, onglet4 = st.tabs(["📊 Calculateur", "🧮 Stratégies", "🏆 Combinés", "🤖 Prédictions IA & Vos Règles"])

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

with onglet1:
    st.header(f"Analyse en direct : {nom_course} ({type_course})")
    
    # ESPACE DE SAISIE À 9 CHIFFRES
    st.subheader("🔢 Saisie de votre base à 9 chiffres maximum")
    chiffres_saisis = st.text_input(
        "Entrez vos numéros séparés par des virgules (ex: 4,5,6,12,13,14,1,2,8) :",
        max_chars=35,
        help="Saisissez jusqu'à 9 chiffres maximum."
    )
    if chiffres_saisis:
        liste_9 = [n.strip() for n in chiffres_saisis.split(",") if n.strip().isdigit()]
        if len(liste_9) > 9:
            st.error(f"⚠️ Vous avez entré {len(liste_9)} numéros. La limite stricte est de 9 chiffres !")
        else:
            st.success(f"✅ Vos {len(liste_9)} numéros enregistrés pour l'analyse : {', '.join(liste_9)}")

    st.divider()
    
    st.subheader("Ajuster les Enjeux Financiers (€)")
    cles_chevaux = list(st.session_state.mises.keys())
    c_la, c_lb = st.columns(2)
    
    with c_la:
        for ch in cles_chevaux[:8]:
            st.session_state.mises[ch] = st.slider(f"Mise {ch}", 50, 50000, int(st.session_state.mises[ch]), 250)
    with c_lb:
        for ch in cles_chevaux[8:]:
            st.session_state.mises[ch] = st.slider(f"Mise {ch}", 50, 50000, int(st.session_state.mises[ch]), 250)
            
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
    
    st.subheader("Répartition Graphique des Enjeux")
    chart = alt.Chart(df_mises).mark_arc(innerRadius=60).encode(
        theta=alt.Theta(field="Mises (€)", type="quantitative"),
        color=alt.Color(field="Cheval", type="nominal"),
        tooltip=["Cheval", "Mises (€)"]
    )
    st.altair_chart(chart, use_container_width=True)
        
    st.subheader("📋 Tableau des Cotes & Probabilités Implicites")
    df_rep = pd.DataFrame({
        "Partant": list(cotes_s.keys()),
        "Mises Déposées (€)": list(st.session_state.mises.values()),
        "Cote Proche": [f"{v:.2f} X" for v in cotes_s.values()],
        "Probabilité Implicite": [f"{(mise / max(1.0, m_totale)) * 100:.1f} %" for mise in st.session_state.mises.values()]
    })
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outil d'Arbitrage Spéculatif")
    cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
  
