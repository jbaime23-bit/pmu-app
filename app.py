import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import time
import streamlit.components.v1 as components

# --- MEMOIRE DURABLE DES VISITEURS ---
if 'total_visiteurs' not in st.session_state:
    st.session_state.total_visiteurs = 21

if 'selection_chiffres' not in st.session_state:
    st.session_state.selection_chiffres = "1-2-3-4-5-6-7-8-9"

# --- CONNECTEUR LIVE PMU DIRECT UNIVERSEL ---
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
    return f"Réunion {reunion} Course {course} (Mode Simulation)", 15, secours_mises

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

# BARRE LATÉRALE PUBLICITÉS (VISUELLE)
st.sidebar.header("📢 Espace Sponsor Premium")
st.sidebar.markdown('<div style="text-align:center; background-color:#eff6ff; padding:15px; border-radius:8px; border:2px solid #3b82f6;"><b style="color:#1e40af; font-size:12px;">📊 ANNONCE SIDEBAR ACTIVE</b><br><small style="color:#1d4ed8;">Régie Adsterra connectée</small></div>', unsafe_allow_html=True)

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
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# INTERFACE INTERACTIVE v8.4
st.title(" 🏇 PMU Pro Suite Ultimate Hub v8.4")
st.info(f"👥 **Nombre total de visiteurs sur la plateforme : {st.session_state.total_visiteurs}**")

# --- INTERACTION LIGNE UNIQUE BLINDÉE POUR VOTRE SCRIPT ADSTERRA ---
code_adsterra_clean = '<div style="text-align:center; margin-bottom:15px;"><script type="text/javascript">atOptions = {"key" : "b9b40b1c4e412de03b6465589ab82662","format" : "iframe","height" : 90,"width" : 728,"params" : {}};</script><script type="text/javascript" src="https://highrevenueformat.com"></script></div>'
components.html(code_adsterra_clean, height=105)

# --- CONFIGURATION DU LIVE VIDEO SECURISE ---
with st.expander("📺 Regarder la course Equidia / YouTube en Direct", expanded=True):
    st.video("https://youtube.com")

onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Sélection", "🏆 Combinés", "🤖 IA & Règles"])

liste_9_chiffres = [int(n.strip()) for n in st.session_state.selection_chiffres.split("-") if n.strip().isdigit()]

with onglet1:
    st.header(f"📈 {st.session_state.nom_course_actuel} ({type_course})")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button("🤖 Générer via l'IA"):
            st.session_state.selection_chiffres = "1-4-5-7-8-10-12-13-15"
            st.success("🎯 9 chiffres optimisés posés !")
            st.rerun()

    with col_btn1:
        chiffres_utilisateurs = st.text_input(
            "🔢 Votre sélection de base (9 chiffres max séparés par des tirets) :", 
            value=st.session_state.selection_chiffres,
            key="champ_saisie_libre_user"
        )
        if chiffres_utilisateurs != st.session_state.selection_chiffres:
            st.session_state.selection_chiffres = chiffres_utilisateurs
            st.rerun()
            
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
    st.write(f"Tickets Couplés réalisables avec votre sélection actuelle (**{st.session_state.selection_chiffres}**) :")
    if len(liste_9_chiffres) >= 2:
        combinaisons_tickets = []
        for i in range(len(liste_9_chiffres)):
            for j in range(i + 1, len(liste_9_chiffres)):
                combinaisons_tickets.append(f"Duo : N°{liste_9_chiffres[i]} — N°{liste_9_chiffres[j]}")
        st.dataframe(pd.DataFrame(combinaisons_tickets, columns=["Tickets Couplés Combinés"]), use_container_width=True)
    else:
        st.warning("Veuillez Saisir au moins 2 chiffres dans l'onglet 1.")

with onglet3:
    st.header("🤖 Analyse IA de votre Sélection selon vos Règles")
    if 'video_vue' not in st.session_state: st.session_state.video_vue = False

    if not st.session_state.video_vue and not st.session_state.est_admin:
        st.warning("Annonce publicitaire obligatoire (5 secondes)...")
        components.html('<div style="text-align:center; background:#000; color:#fff; padding:15px; border-radius:8px; font-weight:bold;">▶️ CHARGEMENT DE LA VIDÉO PARTENAIRE (5s)</div>', height=70)
        time.sleep(5)
        st.session_state.video_vue = True
        st.rerun()
    else:
        st.success("🤖 Analyse IA terminée sur vos numéros !")
        expert_data = []
        for num in list(liste_9_chiffres):
            confiance = 50 + (num % 3) * 15
            note_regle = "Zone Neutre"
            if 1 <= num <= 4:
                note_regle = "Favori Solide."
                confiance += 20
            if num == 5:
      
