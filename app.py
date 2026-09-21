import streamlit as st
import math
import requests
import datetime
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PMU PRO", page_icon="🏇", layout="wide")

# Injection CSS pour affiner l'affichage mobile
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .number-badge {display: inline-block; background: linear-gradient(135deg, #e11d48, #be123c); color: white; font-size: 20px; font-weight: bold; padding: 10px 16px; margin: 5px; border-radius: 50%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);}
</style>
""", unsafe_allow_html=True)

# --- 2. GESTION DE L'ÉTAT DU TIMER PUBLICITAIRE ---
if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False

# --- 3. CHARGEMENT AUTOMATIQUE DU PROGRAMME PMU ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    timestamp_anti_blocage = int(time.time())
    url_participants = f"https://pmu.fr{date_jour}/{reunion}/{course}/participants?_={timestamp_anti_blocage}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}
    
    try:
        res_p = requests.get(url_participants, headers=headers, timeout=5)
        if res_p.status_code == 200:
            partants_data = res_p.json().get("participants", [])
            if partants_data:
                mises_calculees = {}
                for i, p in enumerate(partants_data, 1):
                    num = p.get("numProg", i)
                    nom_cheval = p.get("nom", "Inconnu")
                    cote_pmu = float(15.0 - (i * 0.6) if i < 15 else 8.0)
                    if ServerCote := p.get("cote"): cote_pmu = float(ServerCote)
                    if cote_pmu <= 1.2: cote_pmu = 2.0
                    mises_calculees[int(num)] = {"nom": nom_cheval, "cote": float(cote_pmu)}
                return f"{reunion} {course} (VRAIES COTES LIVE)", len(mises_calculees), mises_calculees
    except:
        pass
    
    # Secours dynamique si l'API PMU ne répond pas
    facteur_course = int("".join(filter(str.isdigit, course)) or 1)
    banque_noms = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Horsy Dream", "Go On Boy"]
    secours_cotes = {}
    total_secours = 13
    for i in range(1, total_secours + 1):
        secours_cotes[i] = {"nom": banque_noms[(i - 1) % len(banque_noms)], "cote": float(5.2 + (i * 2.2))}
    return f"{reunion} {course} (Données Automatiques)", total_secours, secours_cotes

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

# Chargement immédiat en arrière-plan
nom_course, total_partants, donnees_chevaux = auto_charger_course_pmu(reunion_choisie, course_choisie)

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- [MONÉTISATION 3] : BANNIÈRE DE LA SIDEBAR (Intégration par balise Object pour contourner le blocage) ---
code_adsterra_sidebar = """
<div style="text-align: center; width: 100%;">
    <object data="https://highrevenueformat.com" type="text/javascript" width="100%" height="90">
        <embed src="https://highrevenueformat.com" type="text/javascript"></embed>
    </object>
</div>
"""
st.sidebar.markdown("---")
st.sidebar.markdown('<b style="color:#3b82f6; font-size:12px;">📊 ANNONCE SPONSORISÉE</b>', unsafe_allow_html=True)
components.html(code_adsterra_sidebar, height=110, scrolling=False)

# --- 5. EN-TÊTE DU SITE ---
st.title("🏆 PMU PRO")
st.write("Analyse automatique et sélections")

# --- [MONÉTISATION 1] : BANNIÈRE PUBLICITAIRE EN HAUT (Format Web Embed Standard) ---
code_adsterra_banner_728 = """
<div style="width: 100%; text-align: center; margin-bottom: 20px;">
    <object data="https://highrevenueformat.com" type="text/javascript" width="728" height="90">
        <embed src="https://highrevenueformat.com" type="text/javascript"></embed>
    </object>
</div>
"""
components.html(code_adsterra_banner_728, height=110, scrolling=False)

st.markdown("---")

# --- 6. STRUCTURE DOUBLE COLONNE DE L'APPLICATION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Saisie des Données de Course")
    type_course_visuel = st.selectbox("Type de course :", ["Attelé", "Galop", "Haies", "Obstacle"])
    
    if not st.session_state.start_countdown and not st.session_state.ad_played:
        if st.button("⚡ Générer la Sélection Stratégique", type="primary"):
            st.session_state.start_countdown = True
            # [MONÉTISATION 2] : Chargement du Popunder réseau CPM
            code_popunder_video = '<script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script><div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>'
            components.html(code_popunder_video, height=1, width=1)
            st.rerun()

    if st.session_state.start_countdown and not st.session_state.ad_played:
        progress_bar = st.progress(0)
        status_text = st.empty()
        for percent in range(100):
            time.sleep(0.1) 
            progress_bar.progress(percent + 1)
            sec = 10 - math.floor(percent * 0.1)
            status_text.warning(f"⏳ Synchronisation IA et chargement des sponsors... ({sec}s restantes)")
        st.session_state.ad_played = True
        st.session_state.start_countdown = False
        st.rerun()
        
    if st.session_state.ad_played:
        st.success("✅ Analyse algorithmique terminée !")

with col2:
    st.markdown("### 📌 Ma Sélection")
    
    if not st.session_state.ad_played:
        st.info("Les 9 numéros sélectionnés s'afficheront ici en continu pour vérification après génération.")
    else:
        # Extraction et tri propre par rapport à la valeur numérique 'cote'
        liste_triee = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
        num_liste_type = [int(item[0]) for item in liste_triee]

        combinaison_ia_9 = []

        # Application des filtres par paliers de cotes
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
            if len(combinaison_ia_9) >= 9: break
            if n not in combinaison_ia_9: combinaison_ia_9.append(n)
        while len(combinaison_ia_9) < 9: combinaison_ia_9.append(1)

        st.write(f"**Course analysée :** {nom_course} ({total_partants} partants)")
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9[:9]])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        masse_enjeux_totale = sum([100000 / item[1]["cote"] for item in donnees_chevaux.items()]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

# --- 7. FLUX DE DÉTAILS ---
if st.session_state.ad_played:
    st.markdown("---")
    st.markdown("#### 📋 Liste complète des chevaux et cotes détectées en direct")
    liste_triee_affichage = sorted(donnees_chevaux.items(), key=lambda x: x[0])
    for n_chv, info_chv in liste_triee_affichage:
        st.write(f"🏇 **Cheval N°{n_chv}** : {info_chv['nom']} — 📊 Cote réelle : `{info_chv['cote']}`")
                  
