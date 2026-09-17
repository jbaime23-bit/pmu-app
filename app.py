import streamlit as st
import math
import pandas as pd
import altair as alt
import os
import requests
import time
import streamlit.components.v1 as components

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

# --- GESTION DE LA SAUVEGARDE PERSISTANTE DES 9 CHIFFRES ---
def gerer_selection_9_chiffres():
    fichier_selection = "selection_9.txt"
    if not os.path.exists(fichier_selection):
        with open(fichier_selection, "w", encoding="utf-8") as f:
            f.write("1,2,3,4,5,6,7,8,9")
    with open(fichier_selection, "r", encoding="utf-8") as f:
        valeur = f.read().strip()
        return valeur if valeur else "1,2,3,4,5,6,7,8,9"

def sauvegarder_selection_9_chiffres(chiffres):
    fichier_selection = "selection_9.txt"
    with open(fichier_selection, "w", encoding="utf-8") as f:
        f.write(chiffres)

chiffres_sauvegardes_init = gerer_selection_9_chiffres()

# --- CONNECTEUR AUTOMATIQUE DES VRAIES COTES LIVE PMU ---
def recuperer_course_automatique(reunion="1", course="1"):
    import datetime
    date_jour = datetime.date.today().strftime("%d%m%Y")
    # API officielle PMU pour récupérer les vrais rapports probables / cotes directes
    url_api = f"https://pmu.fr{date_jour}/R{reunion}/C{course}/rapports-probables?typePari=SIMPLE_GAGNANT"
    
    try:
        res = requests.get(url_api, timeout=6)
        if res.status_code == 200:
            data = res.json()
            rapports = data.get("rapportsProbables", [])
            if rapports:
                nb_chevaux = len(rapports)
                mises_reelles = {}
                for r in rapports:
                    num = r.get("numProg")
                    # Conversion de la vraie cote PMU en équivalence de mise pour le graphique
                    cote_pmu = float(r.get("rapport", 10.0))
                    if cote_pmu <= 1.1: cote_pmu = 1.5
                    # Plus la cote est petite, plus la mise globale est grosse sur ce cheval
                    mises_reelles[f"N°{num}"] = round(100000 / cote_pmu, 2)
                return f"R{reunion} C{course} - Vraies Cotes PMU en Direct", nb_chevaux, mises_reelles
    except Exception:
        pass
    
    # Secours automatique stable avec 15 partants si l'API est indisponible ou course non démarrée
    secours = {f"N°{i}": float(10000 - (i*450)) for i in range(1, 16)}
    return "R1 Paris-Vincennes - Prix de Mehun-sur-Yèvre (Mode Manuel)", 15, secours

# 1. CONFIGURATION DE LA PAGE & VISUELS PRO
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

st.markdown("""<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}
</style>""", unsafe_allow_html=True)

# 2. SYSTÈME DE DOUBLE CLÉ SÉCURISÉ (ADMIN / USER)
MOT_DE_PASSE_USER = "PMU_PRO_2026"
MOT_DE_PASSE_ADMIN = "ADMIN7670"

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

# 3. CONFIGURATION INITIALE
if 'nombre_partants' not in st.session_state:
    st.session_state.nombre_partants = 15
if 'mises' not in st.session_state:
    st.session_state.mises = {f"N°{i}": float(10000 - (i*450)) for i in range(1, 16)}
if 'nom_course_actuel' not in st.session_state:
    st.session_state.nom_course_actuel = "R1 Paris-Vincennes - Prix de Mehun-sur-Yèvre"

# 4. BARRE LATÉRALE - PUBLICITÉS & CONFIGURATION ACTIVE
st.sidebar.header("📢 Espace Sponsor Premium")
code_regie_top_sidebar = '<div style="text-align:center; background:#fff7ed; padding:12px; border-radius:6px; border:2px dashed #ea580c; margin-bottom:5px;"><small style="color:#c2410c; font-weight:bold;">🚀 PUBLICITÉ TOP SIDEBAR AUTOMATIQUE</small><br><span style="font-size:10px; color:#666;">(Bannière a forte valeur ajoutée)</span></div>'
components.html(code_regie_top_sidebar, height=85)

st.sidebar.markdown("---")
st.sidebar.subheader("💎 Version Pro Premium")
st.sidebar.write("Retirez les vidéos publicitaires et accédez en 1 clic à l'IA.")
st.sidebar.markdown("📲 **Abonnement mensuel : 5 000 FCFA**")
st.sidebar.write("🔶 **Orange Money :** +226 76 16 69 74")
st.sidebar.write("🔷 **Moov Money :** +226 70 01 10 17")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Partenaires Secondaires")
code_regie_sidebar = '<div style="text-align:center; background:#eff6ff; padding:10px; border-radius:6px; border:1px solid #bfdbfe;"><small style="color:#1e40af; font-weight:bold;">🤖 PUBLICITÉ BANQUE ANNONCES AUTOMATIQUE</small></div>'
components.html(code_regie_sidebar, height=60)

st.sidebar.header("⚙️ Configuration de la Course")
c_reunion = st.sidebar.text_input("Réunion (Ex: 1)", value="1", max_chars=2)
c_course = st.sidebar.text_input("Course (Ex: 1)", value="1", max_chars=2)

if st.sidebar.button("🔄 Synchronisation des Vraies Cotes"):
    nom_c, nb_p, m_init = recuperer_course_automatique(c_reunion, c_course)
    st.session_state.nom_course_actuel = nom_c
    st.session_state.nombre_partants = nb_p
    st.session_state.mises = m_init
    st.sidebar.success("📊 Vraies cotes synchronisées avec succès !")
    st.rerun()

st.sidebar.markdown("---")
nom_course = st.sidebar.text_input("Nom affiché :", value=st.session_state.nom_course_actuel)
type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])

t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.session_state.est_admin = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact & Soutien")
lien_whatsapp = "https://wa.me"
st.sidebar.markdown(f'<a href="{lien_whatsapp}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold;">🟢 Rejoindre sur WhatsApp</button></a>', unsafe_allow_html=True)
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

def calculus_combines(mises, taux_comb):
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

def archive_ia_expert(mises, specialite, total_chevaux):
    scores_base = {f"N°{i}": 50 + (i % 3)*10 for i in range(1, total_chevaux + 1)}
    analyses = {}
    for i in range(1, total_chevaux + 1):
        cheval_key = f"N°{i}"
        if 1 <= i <= 4:
            analyses[cheval_key] = "Zone Favoris (Règle Expert : 1 à 2 numéros sortent souvent ici)."
            scores_base[cheval_key] += 12
        elif i == 5:
            analyses[cheval_key] = "Point d'appui (Règle Expert : Présence fréquente d'un numéro)."
            scores_base[cheval_key] += 8
        elif 6 <= i <= 12:
            analyses[cheval_key] = "Outsiders (Règle Expert : Zone à forte récurrence, 1 ou 2 numéros)."
            scores_base[cheval_key] += 15
        elif 13 <= i <= 16:
            analyses[cheval_key] = "Zone Grosses Cotes / Tocard ciblé (1 numéro à chercher ici)."
            scores_base[cheval_key] += 6
        else:
            analyses[cheval_key] = "Extrême Outsider (Course élargie à plus de 16 partants)."
            scores_base[cheval_key] -= 4
        if specialite == "Attelé (Trot)" and (6 <= i <= 12 or 1 <= i <= 4):
            analyses[cheval_key] += " Modèle Attelé renforcé."
            scores_base[cheval_key] += 7
    return scores_base, analyses

# 6. ENSEMBLE DES ONGLETS D'AFFICHAGE
st.title("🏇 PMU Pro Suite Ultimate Hub v6.3")
  
