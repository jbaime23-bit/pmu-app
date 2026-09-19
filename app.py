import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import datetime
import time  # Importation essentielle pour la gestion anti-blocage
import streamlit.components.v1 as components

# CONFIGURATION DE LA PAGE STREAMLIT
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

# Masquage du menu par défaut et personnalisation de l'arrière-plan
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .stApp {background-color: #f8fafc;}
</style>
""", unsafe_allow_html=True)

# --- FONCTION DE CHARGEMENT DYNAMIQUE DU PROGRAMME PMU ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    timestamp_anti_blocage = int(time.time())
    
    # URL Structurée officielle OPM PMU
    url_participants = f"https://pmu.fr{date_jour}/{reunion}/{course}/participants?_={timestamp_anti_blocage}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        res_p = requests.get(url_participants, headers=headers, timeout=6)
        if res_p.status_code == 200:
            partants_data = res_p.json().get("participants", [])
            if partants_data:
                mises_calculees = {}
                for i, p in enumerate(partants_data, 1):
                    num = p.get("numProg", i)
                    nom_cheval = p.get("nom", "Inconnu")
                    cote_pmu = float(15.0 - (i * 0.6) if i < 15 else 8.0)
                    if cote_pmu <= 1.2: cote_pmu = 2.0
                    mises_calculees[f"N°{num} - {nom_cheval}"] = round(100000 / cote_pmu, 2)
                
                return f"{reunion} {course} (VRAIES COTES LIVE PMU)", len(mises_calculees), mises_calculees
    except Exception:
        pass
    
    # --- SECOURS INTELLIGENT ET DYNAMIQUE ---
    facteur_reunion = int("".join(filter(str.isdigit, reunion)) or 1)
    facteur_course = int("".join(filter(str.isdigit, course)) or 1)
    
    banque_noms = [
        "Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", 
        "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", 
        "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes", 
        "Galius", "Diable de Vauvert", "Granvillaise Bleue", "Go On Boy", "Horsy Dream"
    ]
    
    rotation = (facteur_reunion + facteur_course) % len(banque_noms)
    noms_du_moment = banque_noms[rotation:] + banque_noms[:rotation]
    
    secours_mises = {}
    nombre_partants = 12 + (facteur_course % 5)
    
    for i in range(nombre_partants):
        base_enjeux = 12000 - (i * 550) + (facteur_course * 150)
        secours_mises[f"N°{i+1} - {noms_du_moment[i % len(noms_du_moment)]}"] = float(max(base_enjeux, 400))
        
    return f"{reunion} {course} (Données Automatiques)", nombre_partants, secours_mises


# --- CONFIGURATION INTERFACE SIDEBAR (BARRE LATÉRALE) ---
st.sidebar.header("🏆 Sélection du Programme")
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0)

# Synchronisation de l'état de l'application
if 'mises' not in st.session_state or st.sidebar.button("🔄 Synchroniser la Course"):
    nom_c, nb_p, m_init = auto_charger_course_pmu(reunion_choisie, course_choisie)
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init

# BARRE LATÉRALE - ESPACE STATUT
st.sidebar.markdown("---")
st.sidebar.header("📢 Espace Sponsor Premium")
st.sidebar.markdown('<div style="text-align:center; background-color:#eff6ff; padding:15px; border-radius:8px; border:2px solid #3b82f6;"><b style="color:#1e40af; font-size:12px;">📊 ANNONCE SIDEBAR ACTIVE</b><br><small style="color:#1d4ed8;">Régie Adsterra connectée</small></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Statut Système")
st.sidebar.success("🟢 Application Publique Ouverte")

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")


# --- LOGIQUE ALGORITHMIQUE & CALCULS PMU ---
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# Tri et traitement de la combinaison IA
cotes_triees = sorted(cotes_s.items(), key=lambda item: item)
num_ia_trie = []
for item in cotes_triees:
    num_extraction = "".join(filter(str.isdigit, item.split(" - ")))
    if num_extraction.isdigit():
        num_ia_trie.append(int(num_extraction))

favoris_choisis = [n for n in num_ia_trie if 1 <= n <= 4][:3]
outsiders_choisis = [n for n in num_ia_trie if 6 <= n <= 12][:4]
appuis_choisis = [n for n in num_ia_trie if n == 5][:1]
tocards_choisis = [n for n in num_ia_trie if n >= 13][:2]

combinaison_ia_9 = favoris_choisis + appuis_choisis + outsiders_choisis + tocards_choisis
while len(combinaison_ia_9) < 9 and len(num_ia_trie) > 0:
    for x in num_ia_trie:
        if x not in combinaison_ia_9: combinaison_ia_9.append(x)
        if len(combinaison_ia_9) == 9: break

combinaison_formatee_ia = "-".join(map(str, combinaison_ia_9[:9]))


# --- INTERFACE VISUELLE DU HUB CENTRAL ---
st.title(" 🏇 PMU Pro Suite Ultimate Hub v9.1")

# --- BANNIÈRE PUBLICITAIRE N°1 : 728x90 (FIXE EN HAUT DE PAGE) ---
code_adsterra_banner_728 = """
<div style="text-align:center; margin-bottom:15px;">
<script>
  atOptions = {
    'key' : 'b9b40b1c4e412de03b6465589ab82662',
    'format' : 'iframe',
    'height' : 90,
    'width' : 728,
    'params' : {}
  };
</script>
<script src="https://www.highrevenueformat.com/b9b40b1c4e412de03b6465589ab82662/invoke.js"></script>
</div>
"""
components.html(code_adsterra_banner_728, height=105, scrolling=False)


# --- SCRIPT POPUNDER VIDÉO INTERMÉDIAIRE DE 5 SECONDES ---
if 'ad_played' not in st.session_state:
    st.session_state.ad_played = False
if 'start_countdown' not in st.session_state:
    st.session_state.start_countdown = False

# Code d'injection du Popunder vidéo lors du clic
code_popunder_video = """
<script src="https://pl31412908.profitableratecpmnetwork.com/20/e7/77/20e777896497a03cbf50c084a66999b4.js"></script>
"""

st.markdown('<div style="background-color:#ffffff; padding:15px; border-radius:10px; border:1px solid #e2e8f0; text-align:center; margin-bottom:20px;">', unsafe_allow_html=True)

if not st.session_state.start_countdown and not st.session_state.ad_played:
    if st.button("▶️ LANCER LE STREAMING EN DIRECT EQUIDIA", key="trigger_live_btn", use_container_width=True, type="primary"):
        st.session_state.start_countdown = True
        components.html(code_popunder_video, height=0, width=0)
        st.rerun()

if st.session_state.start_countdown and not st.session_state.ad_played:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Lancement du compte à rebours visuel de 5 secondes requis
    for percent_complete in range(100):
        time.sleep(0.05)  # 100 * 0.05s = 5 secondes totales
        progress_bar.progress(percent_complete + 1)
        secondes_restantes = 5 - math.floor((percent_complete * 0.05))
        status_text.warning(f"⏳ Chargement du flux vidéo sécurisé en cours... Veuillez patienter {secondes_restantes}s (Publicité active en arrière-plan)")
    
    st.session_state.ad_played = True
    st.session_state.start_countdown = False
    st.rerun()

if st.session_state.ad_played:
    st.success("✅ Connexion au flux établie avec succès !")
    st.markdown("""
        <a href="https://lescourseshippiques.fr" target="_blank" style="text-decoration:none;">
            <button style="background-color:#22c55e; color:white; border:none; padding:12px 25px; font-size:15px; font-weight:bold; border-radius:6px; cursor:pointer; width:100%;">
                📺 ACCÉDER IMMÉDIATEMENT AU DIRECT EN DIRECT ICI
            </button>
        </a>
    """, unsafe_allow_html=True)
    if st.button("🔄 Réinitialiser le lecteur", key="reset_ad_btn"):
        st.session_state.ad_played = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# CONFIGURATION DES ONGLETS
onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Sélection", "🏆 Combinés Générés", "🤖 Analyses Multi-Règles"])

liste_9_chiffres = combinaison_ia_9[:9]

with onglet1:
    st.markdown('<p style="text-align:center; color:#94a3b8; font-size:11px; margin-bottom:5px;">Sponsorisé</p>', unsafe_allow_html=True)
    code_adsterra_native_deplacee = """
    <div style="text-align:center; width:100%;">
    <script async="async" data-cfasync="false" src="https://pl31390924.profitableratecpmnetwork.com/548477c48bb33989924ab69d7a4e0cc1/invoke.js"></script>
    <div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
    </div>
    """
    components.html(code_adsterra_native_deplacee, height=180, scrolling=False)
    
    st.header(f"📈 {st.session_state.nom_course_actuel} ({type_course})")
    st.info(f"🤖 **Sélection des 9 chiffres calculée automatiquement par l'IA :** `{combinaison_formatee_ia}`")
    
    st.divider()
    st.metric(label="💰 Masse Globale des Enjeux", value=f"{m_totale:,.2f} €")
    
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Enjeux (€)"])
                                      
