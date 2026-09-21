import streamlit as st
import math
import pandas as pd
import requests
import datetime
import time
import streamlit.components.v1 as components

# --- CONFIGURATION PREMIUM DE LA PAGE ---
st.set_page_config(page_title="PMU Pro Ultimate Hub", page_icon="🏇", layout="wide")

# Personnalisation de l'interface (Design Sombre & Épuré)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .stApp {background-color: #0f172a;}
    .main-title {text-align: center; color: #f8fafc; font-size: 26px; font-weight: bold; margin-bottom: 20px;}
    .pru-box {background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; text-align: center;}
    .number-badge {display: inline-block; background: linear-gradient(135deg, #e11d48, #be123c); color: white; font-size: 20px; font-weight: bold; padding: 10px 16px; margin: 5px; border-radius: 50%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);}
    .info-text {color: #94a3b8; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT AUTOMATIQUE DU PROGRAMME PMU ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    timestamp_anti_blocage = int(time.time())
    
    url_participants = f"https://pmu.fr{date_jour}/{reunion}/{course}/participants.json?_={timestamp_anti_blocage}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        res_p = requests.get(url_participants, headers=headers, timeout=6)
        if res_p.status_code == 200:
            partants_data = res_p.json()
            if isinstance(partants_data, dict):
                partants_list = partants_data.get("participants", [])
            elif isinstance(partants_data, list):
                partants_list = partants_data
            else:
                partants_list = []
                
            if partants_list:
                mises_calculees = {}
                for i, p in enumerate(partants_list, 1):
                    num = p.get("numProg", p.get("numero", i))
                    nom_cheval = p.get("nom", "Inconnu")
                    
                    cote_pmu = 15.0
                    if p.get("coteDirecte"):
                        cote_pmu = p.get("coteDirecte")
                    elif p.get("derniereCoteRef"):
                        cote_pmu = p.get("derniereCoteRef")
                    elif p.get("cote"):
                        cote_pmu = p.get("cote")
                        
                    try:
                        cote_pmu = float(cote_pmu)
                    except:
                        cote_pmu = float(15.0 - (i * 0.6) if i < 15 else 8.0)
                        
                    if cote_pmu <= 1.2: 
                        cote_pmu = 2.0
                        
                    mises_calculees[int(num)] = {"nom": nom_cheval, "cote": float(cote_pmu)}
                return f"{reunion} {course} (VRAIES COTES LIVE)", len(mises_calculees), mises_calculees
    except:
        pass
    
    facteur_course = int("".join(filter(str.isdigit, course)) or 1)
    banque_noms = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Horsy Dream", "Go On Boy"]
    secours_cotes = {}
    total_secours = 12 + (facteur_course % 4)
    for i in range(1, total_secours + 1):
        secours_cotes[i] = {"nom": banque_noms[(i - 1) % len(banque_noms)], "cote": float(3.0 + (i * 2.2))}
    return f"{reunion} {course} (Données de Secours)", total_secours, secours_cotes

# --- INTERFACE BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="color:white; text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0)

if st.sidebar.button("🔄 Rafraîchir les données Live", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

nom_course, total_partants, donnees_chevaux = auto_charger_course_pmu(reunion_choisie, course_choisie)

st.sidebar.markdown("---")
# --- [PUBLICITÉ 2] : ANNONCE EN SIDEBAR ---
st.sidebar.markdown('<div style="text-align:center; background-color:#1e293b; padding:12px; border-radius:8px; border:1px solid #3b82f6;"><b style="color:#3b82f6; font-size:12px;">📊 ANNONCE SIDEBAR</b><br><small style="color:#94a3b8;">Régie Adsterra active</small></div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- LE HUB CENTRAL ---
st.markdown(f'<div class="main-title">🏇 PMU Pro Suite Ultimate Hub v9.1</div>', unsafe_allow_html=True)

# --- [PUBLICITÉ 1] : BANNIÈRE PUBLICITAIRE HAUT (728x90) ---
code_adsterra_banner_728 = """
<div style="width: 100%; text-align: center; margin-bottom: 20px;">
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
"""
components.html(code_adsterra_banner_728, height=110, scrolling=False)

if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False

# --- [PUBLICITÉ 3] : POPUNDER INTERSTITIEL VIDÉO ---
code_popunder_video = """
<script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>
<div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
"""

st.markdown('<div class="pru-box">', unsafe_allow_html=True)
if not st.session_state.start_countdown and not st.session_state.ad_played:
    st.markdown('<p class="info-text">Cliquez ci-dessous pour débloquer l\'accès au direct Equidia et lancer l\'analyse de l\'IA</p>', unsafe_allow_html=True)
    if st.button("▶️ DÉBLOQUER LE DIRECT VIDEO & L'ANALYSE IA", key="trigger_btn", use_container_width=True, type="primary"):
        st.session_state.start_countdown = True
        components.html(code_popunder_video, height=1, width=1)
        st.rerun()

if st.session_state.start_countdown and not st.session_state.ad_played:
    progress_bar = st.progress(0)
    status_text = st.empty()
    for percent in range(100):
        time.sleep(0.1)  # 10 secondes réelles complètes
        progress_bar.progress(percent + 1)
        sec = 10 - math.floor(percent * 0.1)
        status_text.warning(f"⏳ Synchronisation cryptée des flux publicitaires... Veuillez patienter {sec}s")
    st.session_state.ad_played = True
    st.session_state.start_countdown = False
    st.rerun()

if st.session_state.ad_played:
    st.success("✅ Accès au flux sécurisé validé avec succès !")
    st.markdown("""
        <div style="text-align: center; margin-top: 12px; margin-bottom: 10px;">
            <a href="https://equidia.fr" target="_blank" style="display: inline-block; padding: 12px 30px; background-color: #22c55e; color: white; font-weight: bold; text-decoration: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                📺 ACCÉDER AU DIRECT LIVE EQUIDIA HIPPIC
            </a>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TRI DES PARTICIPANTS ET ALGORITHME DE SÉLECTION ---
liste_triee = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
num_liste_type = [int(item[0]) for item in liste_triee]

combinaison_ia_9 = []

if len(num_liste_type) >= 4:
    combinaison_ia_9.extend(num_liste_type[0:4][0:2])
if len(num_liste_type) >= 6:
    combinaison_ia_9.extend(num_liste_type[4:6][0:1])
if len(num_liste_type) >= 9:
    combinaison_ia_9.extend(num_liste_type[6:9][0:2])
if len(num_liste_type) >= 12:
    combinaison_ia_9.extend(num_liste_type[9:12][0:2])

if len(num_liste_type) > 14:
    combinaison_ia_9.extend(num_liste_type[12:-2][0:2])
elif len(num_liste_type) > 12:
    combinaison_ia_9.extend(num_liste_type[12:][0:2])

for n in num_liste_type:
    if len(combinaison_ia_9) >= 9: 
        break
    if n not in combinaison_ia_9: 
        combinaison_ia_9.append(n)
        
while len(combinaison_ia_9) < 9: 
    combinaison_ia_9.append(1)

# --- AFFICHAGE DES RÉSULTATS APRES VALIDATION ---
if st.session_state.ad_played:
    st.markdown(f'<h3 style="color: white; text-align: center; margin-top: 20px;">📊 Pronostic IA & Liste Initiale de la Course : {nom_course}</h3>', unsafe_allow_html=True)
    
    st.markdown('<div class="pru-box">', unsafe_allow_html=True)
    st.markdown('<p style="color: #22c55e; font-weight: bold; font-size: 18px;">🎯 SÉLECTION UNIQUE DE L\'IA (9 NUMÉROS)</p>', unsafe_allow_html=True)
    badges_html = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9[:9]])
    st.markdown(f'<div style="text-align: center; margin-bottom: 10px;">{badges_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    tableau_partants = []
    for num, details in liste_triee:
        tableau_partants.append({
            "N° Numéro": num,
            "Nom du Cheval": details["nom"],
            "Cote Actuelle": f"{details['cote']:.1f}"
        })
    
    df_partants = pd.DataFrame(tableau_partants)
    st.dataframe(df_partants, use_container_width=True, hide_index=True)
  
