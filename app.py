import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import time
import random
import itertools
import re
import datetime
import streamlit.components.v1 as components

# --- MEMOIRE DURABLE DES VISITEURS ---
if 'total_visiteurs' not in st.session_state:
    st.session_state.total_visiteurs = 21

if 'selection_chiffres' not in st.session_state:
    st.session_state.selection_chiffres = "1-2-3-4-5-6-7-8-9"

if 'pub_video_regardee' not in st.session_state:
    st.session_state.pub_video_regardee = False

# --- FONCTION COMPAGNON : EXTRACTION SÉCURISÉE DU NUMÉRO ---
def extraire_un_numero(texte):
    """
    Extrait proprement le premier nombre trouvé dans une chaîne de texte.
    Si aucun numéro n'est trouvé, renvoie 1 par défaut.
    """
    chiffres = re.findall(r'\d+', str(texte))
    if chiffres:
        return int(chiffres[0])
    return 1

# --- ALGORITHME AUTOMATISÉ BASÉ SUR VOS REMARQUES ---
def generer_9_chiffres_depuis_remarques(mises_dict, specialite):
    """
    Automatise la sélection de 9 chiffres maximum en fonction des règles et remarques de l'auteur.
    """
    numeros_disponibles = []
    for k in mises_dict.keys():
        numeros_disponibles.append(extraire_un_numero(k))
            
    if not numeros_disponibles:
        return "1-2-3-4-5-6-7-8-9"
        
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
    except Exception:
        pass
    noms_secours = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes"]
    secours_mises = {f"N°{i+1} - {noms_secours[i]}": float(10000 - (i*600)) for i in range(len(noms_secours))}
    return f"Réunion {reunion} Course {course} (Mode Simulation)", 15, secours_mises

# CONFIGURATION PAGE
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

# ACCÈS SÉCURISÉ
if 'authentifie' not in st.session_state: st.session_state.authentifie = False
if 'est_admin' not in st.session_state: st.session_state.est_admin = False

if not st.session_state.authentifie:
    st.title("🔒 Accès Restreint - Plateforme PMU Pro")
    saisie = st.text_input("Clé d'accès :", type="password")
    if saisie == "ADMIN7670":
        st.session_state.authentifie, st.session_state.est_admin = True, True
        st.rerun()
    elif saisie == "PMU_PRO_2026":
        st.session_state.authentifie, st.session_state.est_admin = True, False
        st.rerun()
    st.stop()

# --- AUTOMATISATION PAR DEFAUT DES COURSES DU JOUR ---
if 'mises' not in st.session_state or 'nom_course_actuel' not in st.session_state:
    nom_c, _, m_init = recuperer_donnees_pmu_reelles("1", "1")
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init

# BARRE LATÉRALE
st.sidebar.header("⚙️ Configuration Course")
c_reunion = st.sidebar.text_input("Réunion", value="1")
c_course = st.sidebar.text_input("Course", value="1")

if st.sidebar.button("🔄 Synchroniser manuellement"):
    nom_c, _, m_init = recuperer_donnees_pmu_reelles(c_reunion, c_course)
    st.session_state.nom_course_actuel, st.session_state.mises = nom_c, m_init
    st.session_state.selection_chiffres = generer_9_chiffres_depuis_remarques(m_init, "Attelé (Trot)")
    st.session_state.pub_video_regardee = False
    st.rerun()

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact")
st.sidebar.write("📧 jb.aime23@gmail.com")

# CALCULATEUR MATHÉMATIQUE
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# INTERFACE INTERACTIVE
st.title(" 🏇 PMU Pro Suite Ultimate Hub v8.4")
st.info(f"👥 **Nombre total de visiteurs sur la plateforme : {st.session_state.total_visiteurs}**")

# --- BANNIÈRE PUBLICITAIRE ADSTERRA 728X90 ---
st.markdown("### 📢 Partenaire Officiel")
code_adsterra = """
<div style="text-align:center; width:100%;">
    <script type="text/javascript">
        atOptions = {
            'key' : 'b9b40b1c4e412de03b6465589ab82662',
            'format' : 'iframe',
            'height' : 90,
            'width' : 728,
            'params' : {}
        };
    </script>
    <script type="text/javascript" src="//://highrevenueformat.com"></script>
</div>
"""
components.html(code_adsterra, height=105)

# --- ZONE CONTENU : SÉPARATEUR EN DEUX COLONNES ---
col_gauche, col_droite = st.columns([1, 1])

with col_gauche:
    st.subheader(f"📊 Analyse en direct : {st.session_state.nom_course_actuel}")
    
    # Préparation du tableau des données
    donnees_tableau = []
    for k, v in st.session_state.mises.items():
        num_cheval = extraire_un_numero(k)
        nom_cheval = k.split(" - ")[1] if " - " in k else k
        donnees_tableau.append({
            "Numéro": num_cheval,
            "Cheval": nom_cheval,
            "Masse des Enjeux (€)": round(v, 2),
            "Cote Estimée": cotes_s[k]
        })
    df_chevaux = pd.DataFrame(donnees_tableau).sort_values(by="Numéro")
    st.dataframe(df_chevaux, use_container_width=True, hide_index=True)

    # Graphique dynamique Altair
    st.markdown("### 📈 Graphique des Masses d'Enjeux")
    chart = alt.Chart(df_chevaux).mark_bar(color='#1e40af').encode(
        x=alt.X('Numéro:O', title='N° du Cheval'),
        y=alt.Y('Masse des Enjeux (€):Q', title='Enjeux globaux (€)'),
        tooltip=['Numéro', 'Cheval', 'Cote Estimée', 'Masse des Enjeux (€)']
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col_droite:
    st.subheader("📺 Diffusion Equidia Live")
    # Lecteur vidéo live officiel Equidia (via leur lecteur externe ou flux d'intégration public)
    code_equidia = """
    <div style="width:100%; text-align:center;">
        <iframe src="https://equidia.fr" width="100%" height="360" style="border:none; border-radius:8px;" allowfullscreen></iframe>
    </div>
    """
  
