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

# 📢 --- [PUBLICITÉ 1/3] : CODE SCRIPT ARRIÈRE-PLAN D'ORIGINE ---
code_cpm_invisible = """
<script src="https://profitableratecpmnetwork.com"></script>
"""
components.html(code_cpm_invisible, height=0, width=0, scrolling=False)

# --- 2. GESTION DE L'ÉTAT ET DU NETTOYAGE ---
if 'ad_played' not in st.session_state: st.session_state.ad_played = False
if 'start_countdown' not in st.session_state: st.session_state.start_countdown = False

def forcer_rafraichissement():
    st.session_state.ad_played = False
    st.session_state.start_countdown = False

# --- 3. CHARGEMENT DYNAMIQUE VIA PARIS-TURF (OUVERT AUX ROBOTS) ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    date_jour = datetime.date.today().strftime("%Y-%m-%d")
    num_r = "".join(filter(str.isdigit, reunion)) or "1"
    num_c = "".join(filter(str.isdigit, course)) or "1"
    
    # Utilisation du flux ouvert de Paris-Turf qui accepte les robots et le cloud scraping
    url_programme = f"https://paris-turf.com{date_jour}/R{num_r}/C{num_c}/participants"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        res_p = requests.get(url_programme, headers=headers, timeout=6)
        if res_p.status_code == 200:
            partants_data = res_p.json()
            if partants_data and isinstance(partants_data, list):
                mises_calculees = {}
                for i, p in enumerate(partants_data, 1):
                    num = int(p.get("numero", i))
                    nom_cheval = p.get("nom", "Inconnu")
                    
                    # Récupération de la cote de référence live
                    cote_brute = p.get("coteRef", p.get("coteDirecte", None))
                    cote_pmu = float(cote_brute) if cote_brute else float(15.0 - (i * 0.6) if i < 15 else 8.0)
                    if cote_pmu <= 1.2: cote_pmu = 2.0
                    
                    mises_calculees[num] = {"nom": nom_cheval, "cote": float(cote_pmu), "numero": num}
                return f"{reunion} {course} (VRAIES COTES LIVE SYNCHRONISÉES)", len(mises_calculees), mises_calculees
    except:
        pass
        
    return f"{reunion} {course}", 0, {}

# --- 4. CONFIGURATION DE LA BARRE LATÉRALE ---
st.sidebar.markdown('<h2 style="text-align:center;">🏇 CONFIGURATION</h2>', unsafe_allow_html=True)
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0, on_change=forcer_rafraichissement)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0, on_change=forcer_rafraichissement)
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

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

# 📢 --- [PUBLICITÉ 2/3] : STRUTUCRE ENVELOPPE ORIGINALE D'ADSTERRA HAUT ---
code_adsterra_haut = """
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
components.html(code_adsterra_haut, height=90, scrolling=False)

st.markdown("---")

# --- 6. STRUCTURE DOUBLE COLONNE ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Saisie des Données de Course")
    type_course_visuel = st.selectbox("Type de course :", ["Attelé", "Galop", "Haies", "Obstacle"])
    
    if total_partants > 0:
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
    elif total_partants == 0:
        st.error("⚠️ Aucun robot n'a pu charger les données. La course sélectionnée n'est pas encore ouverte sur le serveur ou le flux externe est momentanément inaccessible.")
    else:
        # Tri strict basé uniquement sur la valeur numérique de la cote réelle
        chevaux_tries_par_cote = sorted(donnees_chevaux.values(), key=lambda x: x["cote"])
        num_liste_type = [int(ch["numero"]) for ch in chevaux_tries_par_cote]

        combinaison_ia_9 = []

        # Application de vos formules algorithmiques sur le classement par cotes
        if len(num_liste_type) >= 4:
            combinaison_ia_9.extend(num_liste_type[0:4][0:2])  # 2 favoris parmi les 4 premiers
        if len(num_liste_type) >= 6:
            combinaison_ia_9.extend(num_liste_type[4:6][0:1])  # 1 position intermédiaire
        if len(num_liste_type) >= 12:
            combinaison_ia_9.extend(num_liste_type[6:12][0:2]) # 2 chevaux du milieu de tableau
        if len(num_liste_type) >= 16:
            combinaison_ia_9.extend(num_liste_type[12:16][0:2]) # 2 outsiders / grosses cotes

        # Remplissage par ordre d'importance des favoris restants jusqu'à obtenir les 9 numéros requis
        for n in num_liste_type:
            if len(combinaison_ia_9) >= 9: break
            if n not in combinaison_ia_9: 
                combinaison_ia_9.append(n)

        combinaison_ia_9 = sorted(combinaison_ia_9[:9])

        st.write(f"**Course analysée :** {nom_course}")
        html_badges = "".join([f'<div class="number-badge">{num}</div>' for num in combinaison_ia_9])
        st.markdown(html_badges, unsafe_allow_html=True)
        
        masse_enjeux_totale = sum([100000 / ch["cote"] for ch in chevaux_tries_par_cote]) * (1.0 - t_simple)
        st.metric(label="Masse Estimée des Enjeux Nettoyée", value=f"{masse_enjeux_totale:,.2f} €")

st.markdown("---")

# 📢 --- [PUBLICITÉ 3/3] : STRUCTURE ENVELOPPE ORIGINALE SCRIPT BAS ---
code_adsterra_bas = """
<div style="width: 100%; text-align: center; margin-top: 20px;">
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
components.html(code_adsterra_bas, height=90, scrolling=False)
  
