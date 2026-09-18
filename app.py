import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import time
import random
import re
import datetime
import streamlit.components.v1 as components

if 'selection_chiffres' not in st.session_state:
    st.session_state.selection_chiffres = "1-2-3-4-5-6-7-8-9"

if 'pub_video_regardee' not in st.session_state:
    st.session_state.pub_video_regardee = False

if 'est_admin_connecte' not in st.session_state:
    st.session_state.est_admin_connecte = False

# --- FONCTION COMPAGNON : EXTRACTION SÉCURISÉE DU NUMÉRO ---
def extraire_un_numero(texte):
    chiffres = re.findall(r'\d+', str(texte))
    if chiffres:
        return int(chiffres[0])
    return 1

# --- ALGORITHME AUTOMATISÉ BASÉ SUR VOS REMARQUES ---
def generer_9_chiffres_depuis_remarques(mises_dict, specialite):
    numeros_disponibles = []
    if mises_dict:
        for k in mises_dict.keys():
            numeros_disponibles.append(extraire_un_numero(k))
            
    if not numeros_disponibles:
        numeros_disponibles = list(range(1, 16))
        
    selection = set()
    
    # Règle 1 : Les 4 premiers numéros contiennent 1 ou 2 numéros
    zone_1 = [n for n in numeros_disponibles if 1 <= n <= 4]
    if zone_1:
        try:
            nb_a_prendre = random.choice([1, 2])
            selection.update(random.sample(zone_1, min(len(zone_1), nb_a_prendre)))
        except:
            pass
        
    # Règle 2 : Les 4e et 5e numéros contiennent 1 numéro
    zone_2 = [n for n in numeros_disponibles if 4 <= n <= 5]
    if zone_2:
        try:
            selection.update(random.sample(zone_2, min(len(zone_2), 1)))
        except:
            pass
        
    # Règle 3 : Du 6e au 12e numéro contiennent souvent 1 ou 2 numéros gagnants
    zone_3 = [n for n in numeros_disponibles if 6 <= n <= 12]
    if zone_3:
        try:
            nb_a_prendre_z3 = random.choice([1, 2])
            selection.update(random.sample(zone_3, min(len(zone_3), nb_a_prendre_z3)))
        except:
            pass
        
    # Règle 4 & 5 : Du 13e au 16e numéro (1 grosse cote, ou 2 si c'est une course d'Attelé)
    zone_4 = [n for n in numeros_disponibles if 13 <= n <= 16]
    if zone_4:
        try:
            quota_grosse_cote = 2 if specialite == "Attelé (Trot)" else 1
            selection.update(random.sample(zone_4, min(len(zone_4), quota_grosse_cote)))
        except:
            pass
        
    # Remplissage de sécurité si on a moins de 9 chiffres avec le reste des partants
    tous_les_autres = [n for n in numeros_disponibles if n not in selection]
    while len(selection) < 9 and tous_les_autres:
        choix = random.choice(tous_les_autres)
        selection.add(choix)
        tous_les_autres.remove(choix)
        
    resultat_trie = sorted(list(selection))[:9]
    return "-".join(map(str, resultat_trie))

# --- DÉTECTION AUTOMATIQUE DE LA PROCHAINE COURSE DU JOUR ---
def trouver_course_pmu_actuelle():
    date_jour = datetime.date.today().strftime("%d%m%Y")
    url_programme = f"https://pmu.fr{date_jour}/programme"
    try:
        res = requests.get(url_programme, timeout=5)
        if res.status_code == 200:
            reunions = res.json().get("programme", {}).get("reunions", [])
            maintenant = datetime.datetime.now().timestamp() * 1000
            for r in reunions:
                num_r = str(r.get("numOfficiel", 1))
                for c in r.get("courses", []):
                    num_c = str(c.get("numOfficiel", 1))
                    heure_depart = c.get("heureDepart", 0)
                    if heure_depart > (maintenant - 900000):
                        return num_r, num_c
    except:
        pass
    return "1", "1"

# --- CONNECTEUR LIVE PMU DIRECT UNIVERSEL ---
def recuperer_donnees_pmu_reelles(reunion="1", course="1"):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    url_participants = f"https://pmu.fr{date_jour}/R{reunion}/C{course}/participants"
    url_rapports = f"https://pmu.fr{date_jour}/R{reunion}/C{course}/rapports-probables?typePari=SIMPLE_GAGNANT"
    try:
        res_p = requests.get(url_participants, timeout=5)
        if res_p.status_code == 200:
            partants_data = res_p.json().get("participants", [])
            if partants_data:
                mises_calculees = {}
                res_r = requests.get(url_rapports, timeout=4)
                cotes_dict = {}
                if res_r.status_code == 200:
                    for r in res_r.json().get("rapportsProbables", []):
                        cotes_dict[r.get("numProg")] = float(r.get("rapport", 10.0))
                for i, p in enumerate(partants_data, 1):
                    num = p.get("numProg", i)
                    nom_cheval = p.get("nom", "Inconnu")
                    cote_pmu = cotes_dict.get(num, float(15.0 - (i * 0.5) if i < 15 else 12.0))
                    if cote_pmu <= 1.1: cote_pmu = 1.5
                    mises_calculees[f"N°{num} - {nom_cheval}"] = round(100000 / cote_pmu, 2)
                return f"Réunion {reunion} Course {course} du Jour (PMU Live)", len(mises_calculees), mises_calculees
    except:
        pass
    noms_secours = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes"]
    secours_mises = {f"N°{i+1} - {noms_secours[i]}": float(10000 - (i*600)) for i in range(len(noms_secours))}
    return f"Réunion {reunion} Course {course} (Mode Simulation)", 15, secours_mises

# CONFIGURATION PAGE
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

if 'mises' not in st.session_state or 'nom_course_actuel' not in st.session_state:
    r_auto, c_auto = trouver_course_pmu_actuelle()
    nom_c, _, m_init = recuperer_donnees_pmu_reelles(r_auto, c_auto)
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init
    st.session_state.reunion_actuelle = r_auto
    st.session_state.course_actuelle = c_auto

# BARRE LATÉRALE
st.sidebar.header("⚙️ Configuration Course")
c_reunion = st.sidebar.text_input("Réunion", value=st.session_state.get('reunion_actuelle', "1"))
c_course = st.sidebar.text_input("Course", value=st.session_state.get('course_actuelle', "1"))

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

if st.sidebar.button("🔄 Synchroniser manuellement"):
    nom_c, _, m_init = recuperer_donnees_pmu_reelles(c_reunion, c_course)
    st.session_state.nom_course_actuel, st.session_state.mises = nom_c, m_init
    st.session_state.reunion_actuelle, st.session_state.course_actuelle = c_reunion, c_course
    st.session_state.selection_chiffres = generer_9_chiffres_depuis_remarques(m_init, type_course)
    st.session_state.pub_video_regardee = False
    st.rerun()

# --- PANNEAU DE CONTROLE CACHÉ ---
st.sidebar.markdown("---")
activation_console = st.sidebar.checkbox("Activer la console", value=False)

if activation_console:
    if not st.session_state.est_admin_connecte:
        cle_admin = st.sidebar.text_input("Code secret :", type="password")
        if cle_admin == "ADMIN7670":
            st.session_state.est_admin_connecte = True
            st.rerun()
    else:
        st.sidebar.info("🛠️ Options Administrateur actives")
        if st.sidebar.button("🔒 Quitter le mode contrôle"):
            st.session_state.est_admin_connecte = False
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact")
st.sidebar.write("📧 jb.aime23@gmail.com")

# CALCULATEUR MATHÉMATIQUE
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values()) if mises else 0
    if int(masse_totale) == 0: return {}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# INTERFACE PRINCIPALE
st.title("🏇 PMU Pro Ultimate v8.4")
st.markdown("<p style='color:#1e40af; font-weight:bold; margin-top:-10px; font-size:14px; text-align:center;'>🟢 Plateforme Officielle Connectée en Direct</p>", unsafe_allow_html=True)

# --- ESPACE PUBLICITAIRE COLLÉ EN HAUT ---
st.markdown("### 📢 Partenaire Officiel")
code_adsterra_stable = """
<div style="text-align:center; width:100%; margin-top:-5px;">
    <iframe src="https://profitablecpmrate.com" width="728" height="90" style="border:none; overflow:hidden; background-color:#fafafa;" scrolling="no"></iframe>
</div>
"""
components.html(code_adsterra_stable, height=115, scrolling=False)

# --- FLUX LIVE EQUIDIA ---
st.subheader("📺 Diffusion Equidia Live")
code_equidia = """
<div style="width:100%; text-align:center;">
    <iframe src="https://equidia.fr" width="100%" height="450" style="border:none; border-radius:8px;" allowfullscreen></iframe>
</div>
"""
components.html(code_equidia, height=470)

st.markdown("---")

# --- CONTENU DE LA COURSE ---
st.subheader(f"📊 {st.session_state.nom_course_actuel}")
st.metric(label="💰 Masse Globale des Enjeux", value=f"{m_totale:,.2f} €")

if st.session_state.mises:
    donnees_tableau = []
    for k, v in st.session_state.mises.items():
        num_cheval = extraire_un_numero(k)
        parts = k.split(" - ")
        nom_cheval = parts[1] if len(parts) > 1 else k
        donnees_tableau.append({
            "Numéro": num_cheval,
            "Cheval": nom_cheval,
            "Masse des Enjeux (€)": round(v, 2),
            "Cote Estimée": cotes_s.get(k, 15.0)
        })
  
