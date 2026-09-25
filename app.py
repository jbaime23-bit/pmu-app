import streamlit as st
import math
import requests
import datetime
import time
import streamlit.components.v1 as components
import json  # Remplacement de bs4 par l'outil natif universel

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

# --- 3. EXTRACTION UNIQUE SUR SITE SECONDAIRE PERMISSIF ---
def charger_course_ultra_secondaire(reunion="R1", course="C1"):
    id_unique_course = f"{reunion}_{course}"
    
    if id_unique_course in st.session_state.donnees_courses_verrouillees:
        return st.session_state.donnees_courses_verrouillees[id_unique_course]
    
    # Utilisation d'un flux d'API secondaire épuré souvent au format JSON brut, insensible aux blocages
    url_alternative = f"https://geny.com{reunion}-{course}-data.json"
    headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)"}
    
    try:
        res = requests.get(url_alternative, headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()  # Extraction native ultra-rapide et robuste
            mises_calculees = {}
            
            for index, p in enumerate(data.get("chevaux", []), 1):
                num = p.get("numero", index)
                nom_cheval = p.get("nom", f"Cheval_{num}")
                cote_pmu = float(p.get("cote", 4.0 + (index * 1.2)))
                mises_calculees[int(num)] = {"nom": nom_cheval, "cote": float(cote_pmu)}
            
            if mises_calculees:
                resultat = (f"{reunion} {course} (Cotes Initiales Figées)", len(mises_calculees), mises_calculees)
                st.session_state.donnees_courses_verrouillees[id_unique_course] = resultat
                return resultat
    except:
        pass
    
    # Secours algorithmique fixe identique
    num_r = int("".join(filter(str.isdigit, reunion)) or 1)
    num_c = int("".join(filter(str.isdigit, course)) or 1)
    banque_noms = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet"]
    
    secours_cotes = {}
    for i in range(1, 16):
        cote_calculee = float(3.5 + (i * 1.4) + (num_c * 0.5))
        secours_cotes[i] = {"nom": banque_noms[i % len(banque_noms)], "cote": round(cote_calculee, 1)}
        
    resultat_secours = (f"{reunion} {course} (Base de Données Fixe)", 15, secours_cotes)
    st.session_state.donnees_courses_verrouillees[id_unique_course] = resultat_secours
    return resultat_secours

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0, on_change=forcer_rafraichissement)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0, on_change=forcer_rafraichissement)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

nom_course, total_partants, donnees_chevaux = charger_course_ultra_secondaire(reunion_choisie, course_choisie)

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
    <script type="text/javascript" src="https://highrevenueformat.com"></script>
</div>
"""
components.html(code_adsterra_haut, height=100, scrolling=False)

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
    <script async="async" data-cfasync="false" src="https://pl31390924.profitableratecpmnetwork.com/548477c48bb33989924ab69d7a4e0cc1/invoke.js"></script>
    <div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
</div>
"""
components.html(code_cpm_network_bas, height=120, scrolling=False)
                           
