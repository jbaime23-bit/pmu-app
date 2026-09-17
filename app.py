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

# --- MEMOIRE DURABLE DES VISITEURS ---
if 'total_visiteurs' not in st.session_state:
    st.session_state.total_visiteurs = 21

if 'selection_chiffres' not in st.session_state:
    st.session_state.selection_chiffres = "1-2-3-4-5-6-7-8-9"

# --- ALGORITHME AUTOMATISÉ BASÉ SUR VOS REMARQUES ---
def generer_9_chiffres_depuis_remarques(mises_dict, specialite):
    """
    Automatise la sélection de 9 chiffres maximum en fonction des règles et remarques de l'auteur.
    """
    numeros_disponibles = []
    for k in mises_dict.keys():
        try:
            # Extraction 100% sécurisée du numéro de cheval via Regex
            match = re.findall(r'\d+', k)
            if match:
                numeros_disponibles.append(int(match[0]))
        except:
            continue
            
    if not numeros_disponibles:
        return "1-2-3-4-5-6-7-8-9"
        
    selection = set()
    
    # Règle 1 : Les 4 premiers numéros contiennent 1 ou 2 numéros
    zone_1 = [n for n in numeros_disponibles if 1 <= n <= 4]
    if zone_1:
        selection.update(random.sample(zone_1, min(len(zone_1), random.choice([1, 2]))))
        
    # Règle 2 : Les 4e et 5e numéros contiennent 1 numéro
    zone_2 = [n for n in numeros_disponibles if 4 <= n <= 5]
    if zone_2:
        selection.update(random.sample(zone_2, min(len(zone_2), 1)))
        
    # Règle 3 : Du 6e au 12e numéro contiennent souvent 1 ou 2 numéros gagnants
    zone_3 = [n for n in numeros_disponibles if 6 <= n <= 12]
    if zone_3:
        selection.update(random.sample(zone_3, min(len(zone_3), random.choice([1, 2]))))
        
    # Règle 4 & 5 : Du 13e au 16e numéro (1 grosse cote, ou 2 si c'est une course d'Attelé)
    zone_4 = [n for n in numeros_disponibles if 13 <= n <= 16]
    if zone_4:
        quota_grosse_cote = 2 if specialite == "Attelé (Trot)" else 1
        selection.update(random.sample(zone_4, min(len(zone_4), quota_grosse_cote)))
        
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
    # Va chercher directement les données fraîches du jour sans intervention manuelle
    nom_c, _, m_init = recuperer_donnees_pmu_reelles("1", "1")
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init

# BARRE LATÉRALE PUBLICITÉS (VISUELLE)
st.sidebar.header("📢 Espace Sponsor Premium")
st.sidebar.markdown('<div style="text-align:center; background-color:#eff6ff; padding:15px; border-radius:8px; border:2px solid #3b82f6;"><b style="color:#1e40af; font-size:12px;">📊 ANNONCE SIDEBAR ACTIVE</b><br><small style="color:#1d4ed8;">Régie Adsterra connectée</small></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
c_reunion = st.sidebar.text_input("Réunion", value="1")
c_course = st.sidebar.text_input("Course", value="1")

if st.sidebar.button("🔄 Synchroniser manuellement"):
    nom_c, _, m_init = recuperer_donnees_pmu_reelles(c_reunion, c_course)
    st.session_state.nom_course_actuel, st.session_state.mises = nom_c, m_init
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

# INTERFACE INTERACTIVE v8.4
st.title(" 🏇 PMU Pro Suite Ultimate Hub v8.4")
st.info(f"👥 **Nombre total de visiteurs sur la plateforme : {st.session_state.total_visiteurs}**")

# --- SCRIPT ADSTERRA EMBARQUÉ DANS L'ENCART JAUNE RESPONSIVE ---
import streamlit.components.v1 as components
code_adsterra_secou_ok = """
<div style="width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; text-align: center; margin-bottom: 15px;">
    <div style="display: inline-block; min-width: 728px; background-color: #fef08a; padding: 15px; border-radius: 8px; border: 2px dashed #eab308; text-align: center;">
        <div style="font-weight: bold; color: #854d0e; font-size: 14px; margin-bottom: 8px; font-family: sans-serif;">
            📢 ENCART PUBLICITAIRE BANNIÈRE HAUTE AUTOMATIQUE (ADSTERRA READY)
        </div>
        <script type="text/javascript">
          atOptions = {
            'key' : 'b9b40b1c4e412de03b6465589ab82662',
            'format' : 'iframe',
            'height' : 90,
            'width' : 728,
            'params' : {}
          };
        </script>
        <script type="text/javascript" src="https://highrevenueformat.com"></script>
    </div>
</div>
"""
components.html(code_adsterra_secou_ok, height=170, scrolling=False)

# --- CONFIGURATION DU LIVE VIDEO SECURISE ---
with st.expander("📺 Regarder la course Equidia / YouTube en Direct", expanded=True):
    st.video("https://youtube.com")

onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Sélection", "🏆 Combinés", "🤖 IA & Règles"])

with onglet1:
    st.header(f"📈 {st.session_state.nom_course_actuel} ({type_course})")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button("🤖 Générer via l'IA"):
            selection_ia = generer_9_chiffres_depuis_remarques(st.session_state.mises, type_course)
            st.session_state.selection_chiffres = selection_ia
            st.success(f"🎯 9 chiffres optimisés selon vos remarques : {selection_ia}")
            st.rerun()

    with col_btn1:
        chiffres_utilisateurs = st.text_input(
            "🔢 Votre sélection de base (9 chiffres max séparés par des tirets) :", 
            value=st.session_state.selection_chiffres,
            key="champ_saisie_libre_user"
        )
        if chiffres_utilisateurs != st.session_state.selection_chiffres:
            st.session_state.selection_chiffres = chiffres_utilisateurs
            st.rerun()
            
    st.divider()
    st.metric(label="💰 Masse Globale des Enjeux", value=f"{m_totale:,.2f} €")
    
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Enjeux (€)"])
  
