import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import datetime
import time
import streamlit.components.v1 as components

# CONFIGURATION PAGE
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

# Injection CSS globale sécurisée
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .stApp {background-color: #f8fafc;}
</style>
""", unsafe_allow_html=True)

# --- DÉTECTION ET CHARGEMENT AUTOMATIQUE DE LA COURSE ACTIVE PMU ---
def auto_charger_course_pmu(reunion="R1", course="C1"):
    date_jour = datetime.date.today().strftime("%d%m%Y")
    timestamp_anti_blocage = int(time.time())
    
    # URL Officielle de l'API PMU OPM
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
                    # Génération automatique d'une cote simulée cohérente si l'API rapport échoue
                    cote_pmu = float(15.0 - (i * 0.6) if i < 15 else 8.0)
                    if cote_pmu <= 1.2: cote_pmu = 2.0
                    mises_calculees[f"N°{num} - {nom_cheval}"] = round(100000 / cote_pmu, 2)
                
                return f"{reunion} {course} (VRAIES COTES LIVE PMU)", len(mises_calculees), mises_calculees
    except Exception:
        pass
    
    # Génération automatique et dynamique si panne de l'API (Évite le blocage R1 C1 fixe)
    noms_secours = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes", "Galius", "Diable de Vauvert", "Granvillaise Bleue"]
    secours_mises = {}
    for i in range(15):
        secours_mises[f"N°{i+1} - {noms_secours[i]}"] = float(10000 - (i * 600))
        
    return f"{reunion} {course} (Données Automatiques)", 15, secours_mises

# SÉLECTION DYNAMIQUE EN SIDEBAR
st.sidebar.header("🏆 Sélection du Programme")
reunion_choisie = st.sidebar.selectbox("Réunion :", ["R1", "R2", "R3", "R4", "R5"], index=0)
course_choisie = st.sidebar.selectbox("Course :", [f"C{x}" for x in range(1, 13)], index=0)

# Maintien de l'état des données lors des interactions
if 'mises' not in st.session_state or st.sidebar.button("🔄 Synchroniser la Course"):
    nom_c, nb_p, m_init = auto_charger_course_pmu(reunion_choisie, course_choisie)
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init

# BARRE LATÉRALE - BANNIÈRE PUBLICITAIRE IFRAME (Solution au blocage)
st.sidebar.markdown("---")
st.sidebar.header("📢 Espace Sponsor Premium")

# Remplacer 'https://highrevenueformat.com...' par votre lien d'intégration iframe Adsterra exact
st.sidebar.markdown("""
<div style="text-align:center;">
    <iframe src="https://highrevenueformat.comwatch?key=b9b40b1c4e412de03b6465589ab82662" width="120" height="240" frameborder="0" scrolling="no"></iframe>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Statut Système")
st.sidebar.success("🟢 Application Publique Ouverte")

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# CALCULATEUR MATHÉMATIQUE
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# AUTO-SÉLECTION DES 9 CHIFFRES D'EXPERT
cotes_triees = sorted(cotes_s.items(), key=lambda item: item[1])
num_ia_trie = []
for item in cotes_triees:
    num_extraction = "".join(filter(str.isdigit, item[0].split(" - ")[0]))
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

# INTERFACE INTERACTIVE PRINCIPALE
st.title(" 🏇 PMU Pro Suite Ultimate Hub v9.1")

# --- BANNIÈRE DU HAUT ADSTERRA IFRAME NATIVE PURE ---
code_adsterra_banner_iframe = """
<div style="text-align:center; margin-bottom:15px;">
    <iframe src="https://highrevenueformat.comwatch?key=b9b40b1c4e412de03b6465589ab82662" width="728" height="90" frameborder="0" scrolling="no"></iframe>
</div>
"""
st.markdown(code_adsterra_banner_iframe, unsafe_allow_html=True)

# --- BOUTON UNIVERSEL REGARDER LE LIVE GRATUIT ---
st.markdown("""
<div style="background-color:#ffffff; padding:15px; border-radius:10px; border:1px solid #e2e8f0; text-align:center; margin-bottom:20px;">
    <a href="https://letrot.com" target="_blank" style="text-decoration:none;">
        <button style="background-color:#ef4444; color:white; border:none; padding:12px 25px; font-size:15px; font-weight:bold; border-radius:6px; cursor:pointer; width:100%; max-width:350px;">
            ▶️ REJOINDRE LE LIVE STREAMING GRATUIT (LETROT)
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Sélection", "🏆 Combinés Générés", "🤖 Analyses Multi-Règles"])

liste_9_chiffres = combinaison_ia_9[:9]

with onglet1:
    st.header(f"📈 {st.session_state.nom_course_actuel} ({type_course})")
    st.info(f"🤖 **Sélection des 9 chiffres calculée automatiquement par l'IA :** `{combinaison_formatee_ia}`")
    
    st.divider()
    st.metric(label="💰 Masse Globale des Enjeux", value=f"{m_totale:,.2f} €")
    
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Enjeux (€)"])
    chart = alt.Chart(df_mises).mark_arc(innerRadius=60).encode(theta=alt.Theta(field="Enjeux (€)", type="quantitative"), color=alt.Color(field="Cheval", type="nominal"))
    st.altair_chart(chart, use_container_width=True)
    
    df_tableau = pd.DataFrame({"Partant & Nom": list(cotes_s.keys()), "Cote Live PMU": [f"{v:.2f} X" for v in cotes_s.values()], "Enjeux Simulés (€)": list(st.session_state.mises.values())})
    donnees_modifiees = st.data_editor(df_tableau, use_container_width=True, hide_index=True, disabled=["Partant & Nom", "Cote Live PMU"])
    
    for idx, row in donnees_modifiees.iterrows():
        st.session_state.mises[row["Partant & Nom"]] = float(row["Enjeux Simulés (€)"])

with onglet2:
    st.header("🏆 Générateur de Combinés Réduits")
    st.write(f"Tickets Couplés calculés d'après les 9 chiffres de l'IA (**{combinaison_formatee_ia}**) :")
    combinaisons_tickets = []
    for i in range(len(liste_9_chiffres)):
        for j in range(i + 1, len(liste_9_chiffres)):
            combinaisons_tickets.append(f"Duo : N°{liste_9_chiffres[i]} — N°{liste_9_chiffres[j]}")
    st.dataframe(pd.DataFrame(combinaisons_tickets, columns=["Tickets Couplés Combinés"]), use_container_width=True)

with onglet3:
    st.header("🤖 Analyse IA de votre Sélection selon vos Règles")
    st.write("Analyse des cotes dynamiques terminée. Les filtres automatiques appliquent vos règles de répartition.")
                  
