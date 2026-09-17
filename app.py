import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import time
import streamlit.components.v1 as components

# --- COMPTEUR DE VISITEURS ---
if 'total_visiteurs' not in st.session_state:
    st.session_state.total_visiteurs = 21

# --- CONNECTEUR AUTOMATIQUE SÉCURISÉ ---
def recuperer_course_automatique(reunion="1", course="1"):
    import datetime
    date_jour = datetime.date.today().strftime("%d%m%Y")
    url_api = f"https://pmu.fr{date_jour}/R{reunion}/C{course}/rapports-probables?typePari=SIMPLE_GAGNANT"
    try:
        res = requests.get(url_api, timeout=5)
        if res.status_code == 200:
            data = res.json()
            rapports = data.get("rapportsProbables", [])
            if rapports:
                nb_chevaux = len(rapports)
                mises_reelles = {}
                for r in rapports:
                    num = r.get("numProg")
                    cote_pmu = float(r.get("rapport", 10.0))
                    if cote_pmu <= 1.1: cote_pmu = 1.5
                    mises_reelles[f"N°{num}"] = round(100000 / cote_pmu, 2)
                return f"R{reunion} C{course} - Live PMU", nb_chevaux, mises_reelles
    except Exception:
        pass
    secours = {f"N°{i}": float(10000 - (i*450)) for i in range(1, 16)}
    return "R1 Paris-Vincennes - Prix de Mehun-sur-Yèvre (Manuel)", 15, secours

# PAGE
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

# SÉCURITÉ CLÉ
MOT_DE_PASSE_USER = "PMU_PRO_2026"
MOT_DE_PASSE_ADMIN = "ADMIN7670"

if 'authentifie' not in st.session_state:
    st.session_state.authentifie = False
if 'est_admin' not in st.session_state:
    st.session_state.est_admin = False

def verifier_mot_de_passe():
    saisie = st.session_state["mot_de_passe_saisi"]
    if saisie == MOT_DE_PASSE_ADMIN:
        st.session_state.authentifie = True
        st.session_state.est_admin = True
    elif saisie == MOT_DE_PASSE_USER:
        st.session_state.authentifie = True
        st.session_state.est_admin = False
    else:
        st.error("❌ Clé d'accès incorrecte.")

if not st.session_state.authentifie:
    st.title("🔒 Accès Restreint - Plateforme PMU Pro")
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

# INITIALISATION DATA
if 'nombre_partants' not in st.session_state:
    st.session_state.nombre_partants = 15
if 'mises' not in st.session_state:
    st.session_state.mises = {f"N°{i}": float(10000 - (i*450)) for i in range(1, 16)}
if 'nom_course_actuel' not in st.session_state:
    st.session_state.nom_course_actuel = "R1 Paris-Vincennes - Prix de Mehun-sur-Yèvre"

# BARRE LATÉRALE PUBLICITÉS
st.sidebar.header("📢 Espace Sponsor Premium")
code_regie_top_sidebar = '<div style="text-align:center; background:#fff7ed; padding:12px; border-radius:6px; border:2px dashed #ea580c; margin-bottom:5px;"><small style="color:#c2410c; font-weight:bold;">🚀 PUBLICITÉ TOP SIDEBAR AUTOMATIQUE</small></div>'
components.html(code_regie_top_sidebar, height=85)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration de la Course")
c_reunion = st.sidebar.text_input("Réunion (Ex: 1)", value="1")
c_course = st.sidebar.text_input("Course (Ex: 1)", value="1")

if st.sidebar.button("🔄 Synchronisation des Vraies Cotes"):
    nom_c, nb_p, m_init = recuperer_course_automatique(c_reunion, c_course)
    st.session_state.nom_course_actuel = nom_c
    st.session_state.nombre_partants = nb_p
    st.session_state.mises = m_init
    st.sidebar.success("📊 Cotes synchronisées !")
    st.rerun()

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.session_state.est_admin = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact")
st.sidebar.write("📧 jb.aime23@gmail.com")

# CALCULS
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values())
    if masse_totale == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = masse_totale * (1.0 - taux)
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cotes[cheval] = max(math.floor((masse_net / mise) * 100) / 100, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# AFFICHAGE INTERFACE
st.title(" 🏇 PMU Pro Suite Ultimate Hub v6.5")
st.info(f"👥 **Nombre total de visiteurs sur la plateforme : {st.session_state.total_visiteurs}**")

code_regie_haut = '<div style="text-align:center; background:#fef08a; border:2px dashed #ca8a04; padding:10px; border-radius:8px; margin-bottom:10px;"><span style="color:#854d0e; font-weight:bold;">📢 RÉGIE INTERACTIVE : Flux publicitaire actif</span></div>'
components.html(code_regie_haut, height=50)

onglet1, onglet2, onglet3, onglet4 = st.tabs(["📊 Calculateur", "🧮 Arbitrage", "🏆 Combinés", "🤖 IA & Règles"])

with onglet1:
    st.header(f"📈 {st.session_state.nom_course_actuel} ({type_course})")
    chiffres_saisis = st.text_input("🔢 Saisie de votre sélection de base (9 chiffres max) :", value="1,2,3,4,5,6,7,8,9")
    
    st.divider()
    st.subheader("Répartition Graphique des Enjeux")
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Enjeux Calculés (€)"])
    chart = alt.Chart(df_mises).mark_arc(innerRadius=60).encode(
        theta=alt.Theta(field="Enjeux Calculés (€)", type="quantitative"),
        color=alt.Color(field="Cheval", type="nominal")
    )
    st.altair_chart(chart, use_container_width=True)
        
    st.subheader("📋 Tableau Officiel des Cotes & Probabilités Réelles")
    st.dataframe(pd.DataFrame({
        "Partant": list(cotes_s.keys()),
        "Cote Live PMU": [f"{v:.2f} X" for v in cotes_s.values()],
        "Probabilité Implicite": [f"{(mise / max(1.0, m_totale)) * 100:.1f} %" for mise in st.session_state.mises.values()]
    }), use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outil d'Arbitrage Spéculatif")
    st.info("Sélectionnez un cheval et simulez un pari pour observer l'évolution de la cote réelle.")

with onglet3:
    st.header("🏆 Paris Combinés (Top 8)")
    st.info("Moteur prédictif prêt pour l'analyse des couplés et trios.")

with onglet4:
    st.header("🤖 Prédictions IA & Vos Règles")
    if 'video_vue' not in st.session_state:
        st.session_state.video_vue = False

    if not st.session_state.video_vue and not st.session_state.est_admin:
        st.warning("Annonce sponsorisée obligatoire (5 secondes)...")
        code_video_regie = '<div style="text-align:center; background:#000; color:#fff; padding:20px; border-radius:8px;">▶️ CHARGEMENT DE LA VIDÉO (5s)</div>'
        components.html(code_video_regie, height=80)
        barre_progression = st.progress(0)
        for i in range(100):
            time.sleep(0.05)
            barre_progression.progress(i + 1)
        st.session_state.video_vue = True
        st.rerun()
    else:
        st.success("Analyse IA activée de façon sécurisée.")
        st.write("Règles Expert PMU appliquées au traitement de la course.")
  
