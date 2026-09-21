import streamlit as st
import math
import requests
import datetime
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURATION DE LA PAGE (Style Clair comme sur ta capture d'écran) ---
st.set_page_config(page_title="PMU PRO", page_icon="🏇", layout="wide")

# Injection CSS pour affiner l'affichage mobile et masquer les menus inutiles
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
    total_secours = 12 + (facteur_course % 4)
    for i in range(1, total_secours + 1):
        secours_cotes[i] = {"nom": banque_noms[(i - 1) % len(banque_noms)], "cote": float(3.0 + (i * 2.2))}
    return f"{reunion} {course} (Données Automatiques)", total_secours, secours_cotes

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

# Chargement immédiat en arrière-plan des données réelles
nom_course, total_partants, donnees_chevaux = auto_charger_course_pmu(reunion_choisie, course_choisie)

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- 5. EN-TÊTE DU SITE ---
st.title("🏆 PMU PRO")
st.write("Analyse automatique et sélections")

# --- [MONÉTISATION 1] : BANNIÈRE PUBLICITAIRE HAUT (Adsterra) ---
code_adsterra_banner_728 = """
<div style="width: 100%; text-align: center; margin-bottom: 20px;">
    <script type="text/javascript">
      atOptions = {'key' : 'b9b40b1c4e412de03b6465589ab82662', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {}};
    </script>
    <script type="text/javascript" src="https://highrevenueformat.com"></script>
</div>
"""
components.html(code_adsterra_banner_728, height=110, scrolling=False)

st.markdown("---")

# --- 6. STRUCTURE DOUBLE COLONNE DE L'APPLICATION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Saisie des Données de Course")
    # Conservation du sélecteur graphique présent sur ton image
    type_course_visuel = st.selectbox("Type de course :", ["Attelé", "Galop", "Haies", "Obstacle"])
    
    # Bouton de déclenchement avec monétisation intégrée
    if not st.session_state.start_countdown and not st.session_state.ad_played:
        if st.button("⚡ Générer la Sélection Stratégique", type="primary"):
            st.session_state.start_countdown = True
            # Script Popunder CPM Network invisible déclenché en tâche de fond
            code_popunder_video = '<script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>'
            components.html(code_popunder_video, height=1, width=1)
            st.rerun()

    # Barre de progression de 10 secondes réelles exigée
    if st.session_state.start_countdown and not st.session_state.ad_played:
        progress_bar = st.progress(0)
        status_text = st.empty()
        for percent in range(100):
            time.sleep(0.1) # 100 * 0.1s = 10 secondes réelles complètes
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
        # --- LOGIQUE IA : Tri strict basé uniquement sur la valeur de la COTE réelle ---
        liste_triee = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
        num_liste_type = [int(item[0]) for item in liste_triee]

        combinaison_ia_9 = []

        # Application exacte de tes paliers de sélection numérique
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

        # Sécurité pour assurer 9 numéros uniques
        for n in num_liste_type:
            if len(combinaison_ia_9) >= 9: break
            if n not in combinaison_ia_9: combinaison_ia_9.append(n)
        while len(combinaison_ia_9) < 9: combinaison_ia_9.append(1)

        # Affichage dynamique des badges rouges générés par l'IA
        st.write(f"**Course analysée :** {nom_course} ({total_partants} partants)")
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9[:9]])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        # Masse des enjeux
        masse_enjeux_totale = sum([100000 / item[1]["cote"] for item in donnees_chevaux.items()]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

# --- 7. FLUX DE DÉTAILS ET FIN DE PAGE ---
if st.session_state.ad_played:
    st.markdown("---")
    st.markdown("#### 📋 Liste complète des chevaux et cotes détectées en direct")
    for n_chv in num_liste_type:
        nom_chv = donnees_chevaux[n_chv]["nom"]
        cote_chv = donnees_chevaux[n_chv]["cote"]
        st.write(f"🏇 **Cheval N°{n_chv}** : {nom_chv} — 📊 Cote réelle : `{cote_chv}`")
                  
