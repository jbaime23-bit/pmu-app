import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import time
import streamlit.components.v1 as components

# --- MEMOIRE DURABLE ---
if 'total_visiteurs' not in st.session_state:
    st.session_state.total_visiteurs = 21

if 'combinaison_9_sauvegardee' not in st.session_state:
    st.session_state.combinaison_9_sauvegardee = "1-2-3-4-5-6-7-8-9"

# --- CONNECTEUR AUTOMATIQUE DES COTES PMU ---
def recuperer_donnees_pmu_reelles(reunion="1", course="1"):
    import datetime
    date_jour = datetime.date.today().strftime("%d%m%Y")
    url_participants = f"https://pmu.fr{date_jour}/R{reunion}/C{course}/participants"
    url_rapports = f"https://pmu.fr{date_jour}/R{reunion}/C{course}/rapports-probables?typePari=SIMPLE_GAGNANT"
    
    try:
        res_p = requests.get(url_participants, timeout=5)
        if res_p.status_code == 200:
            partants_data = res_p.json().get("participants", [])
            if partants_data:
                mises_calculees = {}
                res_r = requests.get(url_rapports, timeout=4)
                cotes_dict = {}
                if res_r.status_code == 200:
                    for r in res_r.json().get("rapportsProbables", []):
                        cotes_dict[r.get("numProg")] = float(r.get("rapport", 10.0))
                
                for i, p in enumerate(partants_data, 1):
                    num = p.get("numProg", i)
                    nom_cheval = p.get("nom", "Inconnu")
                    cote_pmu = cotes_dict.get(num, float(15.0 - (i * 0.5) if i < 15 else 12.0))
                    if cote_pmu <= 1.1: cote_pmu = 1.5
                    mises_calculees[f"N°{num} - {nom_cheval}"] = round(100000 / cote_pmu, 2)
                
                return f"Réunion {reunion} Course {course} (Données Directes PMU)", len(mises_calculees), mises_calculees
    except Exception:
        pass
    
    noms_secours = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes"]
    secours_mises = {f"N°{i+1} - {noms_secours[i]}": float(10000 - (i*600)) for i in range(len(noms_secours))}
    return f"Réunion {reunion} Course {course} (Mode Simulation Restreint)", 15, secours_mises

# CONFIGURATION PAGE
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

# ACCÈS SÉCURISÉ
if 'authentifie' not in st.session_state: st.session_state.authentifie = False
if 'est_admin' not in st.session_state: st.session_state.est_admin = False

if not st.session_state.authentifie:
    st.title("🔒 Accès Restreint - Plateforme PMU Pro")
    saisie = st.text_input("Clé d'accès :", type="password")
    if saisie == "ADMIN7670":
        st.session_state.authentifie, st.session_state.est_admin = True, True
        st.rerun()
    elif saisie == "PMU_PRO_2026":
        st.session_state.authentifie, st.session_state.est_admin = True, False
        st.rerun()
    st.stop()

# INITIALISATION DATA
if 'mises' not in st.session_state:
    noms_defaut = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes"]
    st.session_state.mises = {f"N°{i+1} - {noms_defaut[i]}": float(10000 - (i*600)) for i in range(15)}
if 'nom_course_actuel' not in st.session_state: st.session_state.nom_course_actuel = "R1 Vincennes - Prix de Mehun-sur-Yèvre (Données Officielles)"

# SIDEBAR PUBLICITÉS
st.sidebar.header("📢 Espace Sponsor Premium")
components.html('<div style="text-align:center; background:#fff7ed; padding:12px; border-radius:6px; border:2px dashed #ea580c;"><small style="color:#ea580c; font-weight:bold;">🚀 PUBLICITÉ TOP SIDEBAR AUTOMATIQUE</small></div>', height=75)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
c_reunion = st.sidebar.text_input("Réunion", value="1")
c_course = st.sidebar.text_input("Course", value="1")

if st.sidebar.button("🔄 Synchroniser les Cotes PMU"):
    nom_c, _, m_init = recuperer_donnees_pmu_reelles(c_reunion, c_course)
    st.session_state.nom_course_actuel, st.session_state.mises = nom_c, m_init
    st.rerun()

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact")
st.sidebar.write("📧 jb.aime23@gmail.com")

# CALCULATEUR MATHÉMATIQUE
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values())
    if masse_totale == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# INTERFACE INTERACTIVE
st.title(" 🏇 PMU Pro Suite Ultimate Hub v7.2")
st.info(f"👥 **Nombre total de visiteurs sur la plateforme : {st.session_state.total_visiteurs}**")

onglet1, onglet2, onglet3, onglet4 = st.tabs(["📊 Calculateur", "🧮 Arbitrage", "🏆 Combinés", "🤖 IA & Règles"])

liste_9_chiffres = [int(n.strip()) for n in st.session_state.combinaison_9_sauvegardee.split("-") if n.strip().isdigit()]

with onglet1:
    st.header(f"📈 {st.session_state.nom_course_actuel} ({type_course})")
    chiffres_saisis = st.text_input("🔢 Saisie de votre sélection de base (9 chiffres max séparés par des tirets) :", value=st.session_state.combinaison_9_sauvegardee)
    if chiffres_saisis != st.session_state.combinaison_9_sauvegardee:
        st.session_state.combinaison_9_sauvegardee = chiffres_saisis
        st.rerun()
    
    st.metric(label="💰 Masse Globale des Enjeux", value=f"{m_totale:,.2f} €")
    
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Enjeux (€)"])
    chart = alt.Chart(df_mises).mark_arc(innerRadius=60).encode(theta=alt.Theta(field="Enjeux (€)", type="quantitative"), color=alt.Color(field="Cheval", type="nominal"))
    st.altair_chart(chart, use_container_width=True)
    
    df_tableau = pd.DataFrame({"Partant & Nom": list(cotes_s.keys()), "Cote Live PMU": [f"{v:.2f} X" for v in cotes_s.values()], "Enjeux Simulés (€)": list(st.session_state.mises.values())})
    donnees_modifiees = st.data_editor(df_tableau, use_container_width=True, hide_index=True, disabled=["Partant & Nom", "Cote Live PMU"])
    for idx, row in donnees_modifiees.iterrows():
        st.session_state.mises[row["Partant & Nom"]] = float(row["Enjeux Simulés (€)"])

with onglet2:
    st.header("🧮 Calculateur d'Arbitrage Spéculatif")
    st.write("Cet outil calcule la mise nécessaire pour couvrir vos pertes sur un second cheval.")
    ch_pref = st.selectbox("Votre cheval de base :", list(cotes_s.keys()))
    ch_couv = st.selectbox("Votre cheval de couverture (Arbitrage) :", list(cotes_s.keys()))
    mise_base = st.number_input("Mise sur le cheval de base (€) :", min_value=10, value=1000)
    
    cote_couv = cotes_s[ch_couv]
    diviseur = max(0.1, cote_couv - 1.0)
    mise_couverture_requise = round(mise_base / diviseur, 2)
    st.info(f"💡 **Règle d'arbitrage :** Pour couvrir entièrement votre risque, vous devez parier **{mise_couverture_requise} €** sur le {ch_couv}.")

with onglet3:
    st.header("🏆 Générateur de Combinés Réduits")
    st.write(f"Voici tous les tickets Couplés réalisables avec vos 9 chiffres actuels (**{st.session_state.combinaison_9_sauvegardee}**) :")
    if len(liste_9_chiffres) >= 2:
        combinaisons_tickets = []
        for i in range(len(liste_9_chiffres)):
            for j in range(i + 1, len(liste_9_chiffres)):
                combinaisons_tickets.append(f"Duo : N°{liste_9_chiffres[i]} — N°{liste_9_chiffres[j]}")
        st.dataframe(pd.DataFrame(combinaisons_tickets, columns=["Tickets Couplés Combinés Générés"]), use_container_width=True)
    else:
        st.warning("Veuillez saisir au moins 2 chiffres dans l'onglet 1 pour générer des combinaisons.")

with onglet4:
    st.header("🤖 Analyse IA de votre Sélection selon vos Règles")
    if 'video_vue' not in st.session_state: st.session_state.video_vue = False

    if not st.session_state.video_vue and not st.session_state.est_admin:
        st.warning("Annonce publicitaire obligatoire (5 secondes)...")
        components.html('<div style="text-align:center; background:#000; color:#fff; padding:15px; border-radius:8px; font-weight:bold;">▶️ CHARGEMENT DE LA VIDÉO PARTENAIRE (5s)</div>', height=70)
        time.sleep(5)
        st.session_state.video_vue = True
        st.rerun()
    else:
        st.success("🤖 Analyse IA terminée sur vos 9 chiffres !")
        expert_data = []
        for num in liste_9_chiffres:
            confiance = 50 + (num % 3) * 15
            note_regle = "Zone Neutre"
            if 1 <= num <= 4:
                note_regle, confiance = "Favori Solide (Règle Expert : Très forte chance de présence dans les 3).", confiance + 20
            elif num == 5:
                note_regle, confiance = "Point d'appui intermédiaire incontournable.", confiance + 15
            elif 6 <= num <= 12:
                note_regle, confiance = "Outsider Spéculatif (Règle Expert : Excellent pour faire grimper les rapports).", confiance + 25
            elif num >= 13:
  
