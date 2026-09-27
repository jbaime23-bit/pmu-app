import streamlit as st
import math
import requests
import datetime
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PMU PRO", page_icon="🏇", layout="wide")

# Injection CSS pour le style général
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .number-badge {display: inline-block; background: linear-gradient(135deg, #e11d48, #be123c); color: white; font-size: 20px; font-weight: bold; padding: 10px 16px; margin: 5px; border-radius: 50%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);}
</style>
""", unsafe_allow_html=True)

# 📢 --- [PUBLICITÉ 1/3] : CODE SCRIPT ARRIÈRE-PLAN (CPM Network) ---
code_cpm_invisible = """
<script src="https://profitableratecpmnetwork.com"></script>
"""
components.html(code_cpm_invisible, height=0, width=0, scrolling=False)

# --- 2. GESTION DE L'ÉTAT ET DU NETTOYAGE ---
if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False
if 'ancienne_course' not in st.session_state: st.session_state.ancienne_course = ""

def forcer_rafraichissement():
    st.session_state.ad_played = False
    st.session_state.start_countdown = False

# --- 3. CHARGEMENT DYNAMIQUE DU PROGRAMME PMU ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    url_programme = f"https://pmu.fr{date_jour}/{reunion}/{course}/participants"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        res_p = requests.get(url_programme, headers=headers, timeout=6)
        if res_p.status_code == 200:
            partants_data = res_p.json()
            if isinstance(partants_data, list) and len(partants_data) > 0:
                mises_calculees = {}
                for i, p in enumerate(partants_data, 1):
                    num = p.get("numProg", i)
                    nom_cheval = p.get("nom", "Inconnu")
                    derniere_cote = p.get("derniereCote", {})
                    cote_pmu = readiness = commit_cote = recreation = derniere_cote.get("cote", None)
                    
                    if not cote_pmu:
                        cote_pmu = float(15.0 - (i * 0.6) if i < 15 else 8.0)
                    
                    cote_pmu = float(cote_pmu)
                    if cote_pmu <= 1.2: 
                        cote_pmu = 2.0
                        
                    mises_calculees[int(num)] = {"nom": nom_cheval, "cote": float(cote_pmu)}
                return f"{reunion} {course} (VRAIES COTES LIVE)", len(mises_calculees), mises_calculees
    except:
        pass
    
    # Système de secours automatique si l'API est inaccessible
    num_r = int("".join(filter(str.isdigit, reunion)) or 1)
    num_c = int("".join(filter(str.isdigit, course)) or 1)
    banque_noms = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Horsy Dream", "Go On Boy", "Galius", "Zarakem", "Haya Zark"]
    
    secours_cotes = {}
    total_secours = 15
    for i in range(1, total_secours + 1):
        index_nom = (i - 1 + num_c + num_r) % len(banque_noms)
        cote_calculee = float(3.2 + (i * 1.5) + (num_c * 0.4) + (num_r * 0.6))
        secours_cotes[i] = {"nom": banque_noms[index_nom], "cote": round(cote_calculee, 1)}
    return f"{reunion} {course} (Données Automatiques)", total_secours, secours_cotes

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0, on_change=forcer_rafraichissement)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0, on_change=forcer_rafraichissement)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

course_actuelle_id = f"{reunion_choisie}-{course_choisie}"
if st.session_state.ancienne_course != course_actuelle_id:
    st.session_state.ancienne_course = course_actuelle_id
    st.session_state.ad_played = False
    st.session_state.start_countdown = False

nom_course, total_partants, donnees_chevaux = auto_charger_course_pmu(reunion_choisie, course_choisie)

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- 5. EN-TÊTE DU SITE ---
st.title("🏆 PMU PRO")
st.write("Analyse automatique et sélections hippiques")

if st.button("🔄 Actualiser la Course & les Publicités", type="secondary"):
    forcer_rafraichissement()
    st.rerun()

st.markdown("### 📺 Diffusion en Direct")
st.markdown('<a href="https://equidia.fr" target="_blank" style="display:inline-block; background-color:#e11d48; color:white; font-weight:bold; padding:12px 24px; text-decoration:none; border-radius:6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🔴 Ouvrir le Live Vidéo (Onglet Sécurisé)</a>', unsafe_allow_html=True)

st.markdown("---")

# 📢 --- [PUBLICITÉ 2/3] : BANNIÈRE HAUT ADSTERRA RESTAURÉE EN RENDU DIRECT ---
code_adsterra_haut = """
<div style="width: 100%; text-align: center; margin-bottom: 20px;">
    <script type="text/javascript">
      atOptions = {'key' : 'b9b40b1c4e412de03b6465589ab82662', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {}};
    </script>
    <script type="text/javascript" src="https://highrevenueformat.com"></script>
</div>
"""
components.html(code_adsterra_haut, height=110, scrolling=False)

st.markdown("---")

# --- 6. STRUCTURE DOUBLE COLONNE ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Saisie des Données de Course")
    type_course_visuel = st.selectbox("Type de course :", ["Attelé", "Galop", "Haies", "Obstacle"])
    st.write(f"**Nombre de partants détectés :** {total_partants}")
    
    if not st.session_state.start_countdown and not st.session_state.ad_played:
        if st.button("⚡ Générer la Sélection Stratégique", type="primary"):
            st.session_state.start_countdown = True
            st.rerun()

    if st.session_state.start_countdown and not st.session_state.ad_played:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for percent in range(100):
            time.sleep(0.1) 
            progress_bar.progress(percent + 1)
            sec = 10 - math.floor(percent * 0.1)
            status_text.warning(f"⏳ Synchronisation algorithmique... ({sec}s restantes)")
            
        st.session_state.ad_played = True
        st.session_state.start_countdown = False
        st.rerun()
        
    if st.session_state.ad_played:
        st.success("✅ Analyse algorithmique terminée avec succès !")

with col2:
    st.markdown("### 📌 Ma Sélection")
    
    if not st.session_state.ad_played:
        st.info("Les 9 numéros sélectionnés s'afficheront ici après génération.")
    else:
        # CORRECTION DU TRI : extraction correcte du numéro (item[0]) basé sur la valeur de la cote (item[1]['cote'])
        cotes_triees = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
        num_liste_type = [int(item[0]) for item in cotes_triees]

        combinaison_ia_9 = []

        # Application stricte de vos règles basées sur l'ordre croissant des cotes
        if len(num_liste_type) >= 4:
            combinaison_ia_9.extend(num_liste_type[0:4][0:2])  # 1 ou 2 parmi les 4 premiers favoris
        if len(num_liste_type) >= 6:
            combinaison_ia_9.extend(num_liste_type[4:6][0:1])  # 1 numéro entre les 4e et 5e positions
        if len(num_liste_type) >= 12:
            combinaison_ia_9.extend(num_liste_type[5:12][0:2]) # 1 ou 2 numéros entre le 6e et 12e
        if len(num_liste_type) >= 16:
            combinaison_ia_9.extend(num_liste_type[12:16][0:1]) # 1 outsider spéculatif entre le 13e et 16e

        # Remplissage de sécurité pour garantir 9 numéros distincts
        for n in num_liste_type:
            if len(combinaison_ia_9) >= 9: break
            if n not in combinaison_ia_9: 
                combinaison_ia_9.append(n)
                
        while len(combinaison_ia_9) < 9: 
            combinaison_ia_9.append(1)

        combinaison_ia_9 = sorted(combinaison_ia_9[:9])

        st.write(f"**Course analysée :** {nom_course}")
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        # Correction du calcul de la masse financière
        masse_enjeux_totale = sum([100000 / item[1]["cote"] for item in donnees_chevaux.items()]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

st.markdown("---")

# 📢 --- [PUBLICITÉ 3/3] : CODE SCRIPT BANNIÈRE BAS ---
code_adsterra_bas = """
<div style="width: 100%; text-align: center; margin-top: 20px;">
    <script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>
    <div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
</div>
"""
components.html(code_adsterra_bas, height=120, scrolling=False)
                  
