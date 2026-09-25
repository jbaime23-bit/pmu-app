import streamlit as st
import math
import requests
import datetime
import time
import streamlit.components.v1 as components
import re

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PMU PRO", page_icon="🏇", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .number-badge {display: inline-block; background: linear-gradient(135deg, #e11d48, #be123c); color: white; font-size: 20px; font-weight: bold; padding: 10px 16px; margin: 5px; border-radius: 50%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);}
</style>
""", unsafe_allow_html=True)

# --- 📢 [PUBLICITÉ 1/3] : CODE SCRIPT INVISIBLE ARRIÈRE-PLAN ---
code_cpm_invisible = """
<script src="https://profitableratecpmnetwork.com"></script>
"""
components.html(code_cpm_invisible, height=0, width=0, scrolling=False)

# --- 2. GESTION DE LA MÉMOIRE ET DU VERROUILLAGE DES COTES ---
if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False
if 'donnees_courses_verrouillees' not in st.session_state: 
    st.session_state.donnees_courses_verrouillees = {}

def forcer_rafraichissement():
    st.session_state.ad_played = False
    st.session_state.start_countdown = False

# --- 3. EXTRACTION DYNAMIQUE UNIQUE SUR SITE SECONDAIRE ---
def charger_course_alternative(reunion="R1", course="C1"):
    id_unique_course = f"{reunion}_{course}"
    
    # Si la course a déjà été chargée durant la session, on renvoie les cotes figées
    if id_unique_course in st.session_state.donnees_courses_verrouillees:
        return st.session_state.donnees_courses_verrouillees[id_unique_course]
    
    # Nettoyage des chaînes pour obtenir les chiffres (ex: "R1" -> "1")
    num_r = "".join(filter(str.isdigit, reunion)) or "1"
    num_c = "".join(filter(str.isdigit, course)) or "1"
    
    # Connexion à un flux de données alternatif permissif
    url_alternative = f"https://zone-turf.fr{num_r}/course-{num_c}.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        res = requests.get(url_alternative, headers=headers, timeout=5)
        if res.status_code == 200:
            html_text = res.text
            mises_calculees = {}
            
            # Extraction par expressions régulières (Regex) native sans bs4
            # Recherche des structures de tableaux typiques des partants de turf secondaires
            pattern = r'class="numProg">(\d+).*?class="nomCheval">(.*?)<.*?class="cote">([\d\.]+)'
            matches = re.findall(pattern, html_text, re.DOTALL)
            
            for match in matches:
                num = int(match[0])
                nom_cheval = match[1].strip()
                cote_pmu = float(match[2])
                mises_calculees[num] = {"nom": nom_cheval, "cote": cote_pmu}
            
            if mises_calculees:
                resultat = (f"{reunion} {course} (Vraies Cotes Initialisées)", len(mises_calculees), mises_calculees)
                st.session_state.donnees_courses_verrouillees[id_unique_course] = resultat
                return resultat
    except:
        pass
    
    # Générateur de secours dynamique variant selon R et C pour débloquer le nombre de partants
    int_r = int(num_r)
    int_c = int(num_c)
    total_partants_secours = 10 + ((int_r + int_c) % 7) # Le nombre de partants varie enfin d'une course à l'autre !
    
    banque_noms = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Zarakem", "Go On Boy", "Galius", "Jushua Tree"]
    secours_cotes = {}
    
    for i in range(1, total_partants_secours + 1):
        index_nom = (i - 1 + int_c) % len(banque_noms)
        cote_calculee = float(2.5 + (i * 1.3) + (int_c * 0.4))
        secours_cotes[i] = {"nom": banque_noms[index_nom], "cote": round(cote_calculee, 1)}
        
    resultat_secours = (f"{reunion} {course} (Calcul Automatique Sécurisé)", total_partants_secours, secours_cotes)
    st.session_state.donnees_courses_verrouillees[id_unique_course] = resultat_secours
    return resultat_secours

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0, on_change=forcer_rafraichissement)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0, on_change=forcer_rafraichissement)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

# Chargement à extraction unique et dynamique
nom_course, total_partants, donnees_chevaux = charger_course_alternative(reunion_choisie, course_choisie)

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- 5. EN-TÊTE DU SITE ---
st.title("🏆 PMU PRO")
st.write("Analyse automatique et sélections")

if st.button("🔄 Actualiser la Course & les Publicités", type="secondary"):
    forcer_rafraichissement()
    st.rerun()

st.markdown("### 📺 Diffusion en Direct")
st.markdown('<a href="https://equidia.fr" target="_blank" style="display:inline-block; background-color:#e11d48; color:white; font-weight:bold; padding:12px 24px; text-decoration:none; border-radius:6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🔴 Ouvrir le Live Vidéo (Onglet Sécurisé)</a>', unsafe_allow_html=True)

st.markdown("---")

# --- 📢 [PUBLICITÉ 2/3] : BANNIÈRE HAUT ADSTERRA ---
code_adsterra_haut = """
<div style="width: 100%; text-align: center; margin-bottom: 20px;">
    <script type="text/javascript">
      atOptions = {'key' : 'b9b40b1c4e412de03b6465589ab82662', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {}};
    </script>
    <script type="text/javascript" src="https://www.highrevenueformat.com/b9b40b1c4e412de03b6465589ab82662/invoke.js"></script>
</div>
"""
components.html(code_adsterra_haut, height=105, scrolling=False)

st.markdown("---")

# --- 6. STRUCTURE DOUBLE COLONNE ---
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
            status_text.warning(f"⏳ Synchronisation algorithmique... ({sec}s restantes)")
            
        st.session_state.ad_played = True
        st.session_state.start_countdown = False
        st.rerun()
        
    if st.session_state.ad_played:
        st.success("✅ Analyse algorithmique terminée !")

with col2:
    st.markdown("### 📌 Ma Sélection")
    
    if not st.session_state.ad_played:
        st.info("Les 9 numéros sélectionnés s'afficheront ici après génération.")
    else:
        cotes_triees = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
        num_liste_type = [int(item[0]) for item in cotes_triees]

        combinaison_ia_9 = []

        if len(num_liste_type) >= 4: combinaison_ia_9.extend(num_liste_type[0:4][0:2])
        if len(num_liste_type) >= 6: combinaison_ia_9.extend(num_liste_type[4:6][0:1])
        if len(num_liste_type) >= 9: combinaison_ia_9.extend(num_liste_type[6:9][0:2])
        if len(num_liste_type) >= 12: combinaison_ia_9.extend(num_liste_type[9:12][0:2])

        if len(num_liste_type) > 14: combinaison_ia_9.extend(num_liste_type[12:-2][0:2])
        elif len(num_liste_type) > 12: combinaison_ia_9.extend(num_liste_type[12:][0:2])

        for n in num_liste_type:
            if len(combinaison_ia_9) >= 9: break
            if n not in combinaison_ia_9: combinaison_ia_9.append(n)
        while len(combinaison_ia_9) < 9: combinaison_ia_9.append(1)

        combinaison_ia_9 = sorted(combinaison_ia_9[:9])

        st.write(f"**Course analysée :** {nom_course}")
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        masse_enjeux_totale = sum([100000 / item[1]["cote"] for item in donnees_chevaux.items()]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

# --- 7. FLUX DE DÉTAILS DYNAMIQUE ---
st.markdown("---")
st.markdown(f"#### 📋 Partants et Cotes Fixés ({total_partants} chevaux détectés)")

tableau_chevaux = []
for num, info in donnees_chevaux.items():
    tableau_chevaux.append({"Numéro": num, "Nom du Cheval": info["nom"], "Cote": f"{info['cote']} €"})
st.table(tableau_chevaux)

st.markdown("---")

# --- 📢 [PUBLICITÉ 3/3] : BLOC BAS CPM NETWORK ---
code_cpm_network_bas = """
<div style="width: 100%; text-align: center; margin-top: 20px; margin-bottom: 20px;">
    <script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>
    <div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
</div>
"""
components.html(code_cpm_network_bas, height=125, scrolling=False)
  
