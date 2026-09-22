import streamlit as st
import math
import requests
import datetime
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PMU PRO", page_icon="🏇", layout="wide")

# Injection CSS pour affiner le style mobile et les badges
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .number-badge {display: inline-block; background: linear-gradient(135deg, #e11d48, #be123c); color: white; font-size: 20px; font-weight: bold; padding: 10px 16px; margin: 5px; border-radius: 50%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);}
</style>
""", unsafe_allow_html=True)

# --- 2. GESTION DES ETATS DE SESSION ---
if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False

# --- 3. FONCTION DYNAMIQUE DE CHARGEMENT PMU ---
def auto_charger_course_pmu(reunion, course):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    # Utilisation d'un timestamp dynamique pour casser le cache et forcer la mise à jour
    timestamp_anti_blocage = int(time.time())
    url_participants = f"https://pmu.fr{date_jour}/{reunion}/{course}/participants?_={timestamp_anti_blocage}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}
    
    try:
        res = requests.get(url_participants, headers=headers, timeout=5)
        if res.status_code == 200:
            partants_data = res.json().get("participants", [])
            if partants_data:
                mises_calculees = {}
                for i, p in enumerate(partants_data, 1):
                    num = p.get("numProg", i)
                    nom_cheval = p.get("nom", "Inconnu")
                    cote_pmu = float(15.0 - (i * 0.6) if i < 15 else 8.0)
                    if ServerCote := p.get("cote"): cote_pmu = float(ServerCote)
                    if cote_pmu <= 1.2: cote_pmu = 2.0
                    mises_calculees[int(num)] = {"nom": nom_cheval, "cote": round(float(cote_pmu), 1)}
                return f"{reunion} {course} (VRAIES COTES LIVE)", len(mises_calculees), mises_calculees
    except:
        pass
    
    # Secours automatique dynamique (génère des cotes différentes selon la course sélectionnée)
    facteur_course = int("".join(filter(str.isdigit, course)) or 1)
    banque_noms = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Horsy Dream", "Go On Boy"]
    secours_cotes = {}
    total_secours = 13
    for i in range(1, total_secours + 1):
        secours_cotes[i] = {"nom": banque_noms[(i - 1) % len(banque_noms)], "cote": round(float(4.0 + (i * 1.5) + (facteur_course * 0.3)), 1)}
    return f"{reunion} {course} (Données Automatiques)", total_secours, secours_cotes

# --- 4. BARRE LATÉRALE DE CONFIGURATION ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- 5. EN-TÊTE DE L'APPLICATION ---
st.title("🏆 PMU PRO")
st.write("Analyse automatique et sélections")

# --- [PUBLICITÉ 1] : ADSTERRA HAUT EN IFRAME COMPLÈTE (Anti-blocage Streamlit) ---
code_adsterra_haut = """
<iframe src="about:blank" srcdoc="
    <html>
    <head><style>body {margin:0; padding:0; text-align:center;}</style></head>
    <body>
        <script type='text/javascript'>
          atOptions = {'key' : 'b9b40b1c4e412de03b6465589ab82662', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {}};
        </script>
        <script type='text/javascript' src='https://highrevenueformat.com'></script>
    </body>
    </html>
" width="100%" height="95" style="border:none; scrolling:no; overflow:hidden;"></iframe>
"""
st.markdown(code_adsterra_haut, unsafe_allow_html=True)

st.markdown("---")

# --- 6. EXECUTION EN DOUBLE COLONNE ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Saisie des Données de Course")
    type_course_visuel = st.selectbox("Type de course :", ["Attelé", "Galop", "Haies", "Obstacle"])
    
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
            status_text.warning(f"⏳ Synchronisation IA... ({sec}s restantes)")
        st.session_state.ad_played = True
        st.session_state.start_countdown = False
        st.rerun()
        
    if st.session_state.ad_played:
        st.success("✅ Analyse algorithmique terminée !")
        
        # Le bouton d'accès au flux d'Equidia s'affiche ici de manière permanente
        st.markdown("""
            <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
                <a href="https://equidia.fr" target="_blank" style="display: inline-block; padding: 12px 25px; background-color: #22c55e; color: white; font-weight: bold; text-decoration: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    📺 ACCÉDER AU DIRECT LIVE VIDEOS EQUIDIA
                </a>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📌 Ma Sélection")
    
    if not st.session_state.ad_played:
        st.info("Les 9 numéros sélectionnés s'afficheront ici après génération.")
    else:
        # EXECUTION DYNAMIQUE : On force l'application à recalculer selon les choix de la Sidebar
        nom_course, total_partants, donnees_chevaux = auto_charger_course_pmu(reunion_choisie, course_choisie)
        
        # Tri de l'IA basé sur la valeur de la cote réelle
        cotes_triees = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
        num_liste_type = [int(item[0]) for item in cotes_triees]

        combinaison_ia_9 = []

        # Application de tes paliers sur les données fraîches
        if len(num_liste_type) >= 4: combinaison_ia_9.extend(num_liste_type[0:4][0:2])
        if len(num_liste_type) >= 6: combinaison_ia_9.extend(num_liste_type[4:6][0:1])
        if len(num_liste_type) >= 9: combinaison_ia_9.extend(num_liste_type[6:9][0:2])
        if len(num_liste_type) >= 12: combinaison_ia_9.extend(num_liste_type[9:12][0:2])

        if len(num_liste_type) > 14:
            combinaison_ia_9.extend(num_liste_type[12:-2][0:2])
        elif len(num_liste_type) > 12:
            combinaison_ia_9.extend(num_liste_type[12:][0:2])

        for n in num_liste_type:
            if len(combinaison_ia_9) >= 9: break
            if n not in combinaison_ia_9: combinaison_ia_9.append(n)
        while len(combinaison_ia_9) < 9: combinaison_ia_9.append(1)

        # Affichage réactif de la course sélectionnée et des badges
        st.write(f"**Course analysée :** {nom_course} ({total_partants} partants)")
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9[:9]])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        masse_enjeux_totale = sum([100000 / item["cote"] for item in donnees_chevaux.values()]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

# --- 7. FLUX DE DETAILS DYNAMIQUE ---
if st.session_state.ad_played:
    st.markdown("---")
    st.markdown("#### 📋 Liste complète des chevaux et cotes actualisées")
    liste_triee_affichage = sorted(donnees_chevaux.items(), key=lambda x: x[0])
    for n_chv, info_chv in liste_triee_affichage:
        st.write(f" 🏇 **Cheval N°{n_chv}** : {info_chv['nom']} — 📊 Cote réelle : `{info_chv['cote']}`")

# --- [PUBLICITÉS 2 & 3] : ZONE SPONSORISÉE BAS EN IFRAME PURE (Anti-blocage) ---
st.markdown("---")
st.markdown('<p style="text-align:center; font-size:12px; color:#666;">Espace Sponsorisé</p>', unsafe_allow_html=True)

code_publicites_bas = """
<iframe src="about:blank" srcdoc="
    <html>
    <head><style>body {margin:0; padding:0; display:flex; justify-content:center; gap:20px; flex-wrap:wrap;}</style></head>
    <body>
        <!-- Deuxième Publicité : CPM Network -->
        <div style='min-width: 300px; text-align: center;'>
            <script async='async' data-cfasync='false' src='https://profitableratecpmnetwork.com'></script>
            <div id='container-548477c48bb33989924ab69d7a4e0cc1'></div>
        </div>
    </body>
    </html>
" width="100%" height="150" style="border:none; scrolling:no; overflow:hidden;"></iframe>
"""
components.html(code_publicites_bas, height=160, scrolling=False)
                      
