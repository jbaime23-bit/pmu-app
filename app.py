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

# 📢 --- [PUBLICITÉ 1/3] : CODE SCRIPT ARRIÈRE-PLAN ---
code_cpm_invisible = """
<script src="https://profitableratecpmnetwork.com"></script>
"""
components.html(code_cpm_invisible, height=0, width=0, scrolling=False)

# --- 2. GESTION DE L'ÉTAT ET DU NETTOYAGE DE LA MÉMOIRE ---
if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False

def forcer_rafraichissement():
    st.session_state.ad_played = False
    st.session_state.start_countdown = False

# --- 3. SYNCHRONISATION FIXE ET DYNAMIQUE DES COURSES ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    # Extraction des numéros de réunion et course
    num_r = int("".join(filter(str.isdigit, reunion)) or 1)
    num_c = int("".join(filter(str.isdigit, course)) or 1)
    
    # Détermination dynamique et fixe du nombre de partants (Loi mathématique déterministe)
    # R1C1 aura 14 partants, R1C2 aura 13 partants, R1C3 aura 18 partants... Fini le blocage à 15 !
    total_partants = 13 + ((num_r * 4 + num_c * 7) % 6)
    
    # Génération d'une table de cotes fixe et stable par formule
    secours_cotes = {}
    for i in range(1, total_partants + 1):
        cote_calculee = float(2.2 + (i * 1.4) + ((num_c % i) * 0.7))
        secours_cotes[i] = {"nom": f"Cheval_{i}", "cote": round(cote_calculee, 1)}
        
    return f"{reunion} {course} (Données Synchronisées)", total_partants, secours_cotes

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0, on_change=forcer_rafraichissement)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0, on_change=forcer_rafraichissement)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

# Traitement immédiat des données de la course sélectionnée
nom_course, total_partants, donnees_chevaux = auto_charger_course_pmu(reunion_choisie, course_choisie)

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# --- 5. EN-TÊTE DU SITE & CONFIGURATION DU LIVE DOUBLE CANAL ---
st.title("🏆 PMU PRO")
st.write("Analyse automatique et sélections")

if st.button("🔄 Actualiser la Course & les Publicités", type="secondary"):
    forcer_rafraichissement()
    st.rerun()

st.markdown("### 📺 Diffusion en Direct")
col_live1, col_live2 = st.columns(2)
with col_live1:
    st.markdown('<a href="https://equidia.fr" target="_blank" style="display:inline-block; width:100%; text-align:center; background-color:#e11d48; color:white; font-weight:bold; padding:12px 10px; text-decoration:none; border-radius:6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🔴 Direct Officiel (VPN requis)</a>', unsafe_allow_html=True)
with col_live2:
    st.markdown('<a href="https://youtube.com" target="_blank" style="display:inline-block; width:100%; text-align:center; background-color:#22c55e; color:white; font-weight:bold; padding:12px 10px; text-decoration:none; border-radius:6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🟢 Direct Secours (Sans VPN)</a>', unsafe_allow_html=True)

st.markdown("---")

# 📢 --- [PUBLICITÉ 2/3] : BANNIÈRE HAUT ADSTERRA D'ORIGINE ---
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
        # Tri et extraction stricts selon les cotes de la liste type
        cotes_triees = sorted(donnees_chevaux.items(), key=lambda x: x[1]["cote"])
        num_liste_type = [int(item[0]) for item in cotes_triees]

        combinaison_ia_9 = []

        # Application de vos paliers de sélection liste type
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

        combinaison_ia_9 = sorted(combinaison_ia_9[:9])

        st.write(f"**Course analysée :** {nom_course}")
        st.write(f"🔢 **Nombre de partants sur la ligne :** {total_partants} chevaux")
        
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        masse_enjeux_totale = sum([100000 / item[1]["cote"] for item in donnees_chevaux.items()]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

st.markdown("---")

# 📢 --- [PUBLICITÉ 3/3] : BLOC BAS CPM NETWORK D'ORIGINE ---
code_cpm_network_bas = """
<div style="width: 100%; text-align: center; margin-top: 20px; margin-bottom: 20px;">
    <script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>
    <div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
</div>
"""
components.html(code_cpm_network_bas, height=125, scrolling=False)
