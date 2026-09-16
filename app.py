import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="PMU Pro", page_icon="🏇", layout="wide")

st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;} .pub-banner {background-color: #fef08a; border: 2px dashed #ca8a04; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; color: #854d0e; font-weight: bold;} .pub-sidebar {background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; text-align: center; border-radius: 6px; margin-top: 20px; color: #1e40af;}</style>""", unsafe_allow_html=True)

MOT_DE_PASSE_CORRECT = "PMU_PRO_2026"
if 'authentifie' not in st.session_state:
    st.session_state.authentifie = False

def verifier_mot_de_passe():
    if st.session_state["mot_de_passe_saisi"] == MOT_DE_PASSE_CORRECT:
        st.session_state.authentifie = True
    else:
        st.error("❌ Mot de passe incorrect.")

if not st.session_state.authentifie:
    st.title("🔒 Accès Restreint - Plateforme PMU Pro")
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

st.markdown("""<div class="pub-banner">📢 BANNIÈRE PUBLICITAIRE DISPONIBLE<br><span style="font-size: 0.85em; font-weight: normal;">Boostez vos paris ou promouvez vos services ici ! Contactez l'administrateur pour louer cet espace.</span></div>""", unsafe_allow_html=True)

def calculer_jeu_simple(mises, taux=0.15):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0:
        return {k: 99.0 for k in mises.keys()}
    masse_net = float(masse_totale) * (1.0 - float(taux))
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cote = math.floor((masse_net / float(mise)) * 100) / 100
            cotes[cheval] = max(cote, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes

def calculer_couples(mises, taux_combine=0.18):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0:
        return {}
    masse_net = masse_totale * (1 - taux_combine)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    cotes_couples = {}
    chevaux = list(mises.keys())
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p1, p2 = probabilites[c1], probabilites[c2]
            if p1 > 0 and p2 > 0:
                p_comb = (p1 * (p2 / max(0.01, 1 - p1))) + (p2 * (p1 / max(0.01, 1 - p2)))
                cote = math.floor((masse_net / max(1.0, masse_net * p_comb * 0.4)) * 100) / 100
                cotes_couples[f"{c1} - {c2}"] = max(cote, 2.0)
    return cotes_couples

if 'mises' not in st.session_state:
    st.session_state.mises = {"N°1": 12000.0, "N°2": 8000.0, "N°3": 4500.0, "N°4": 2000.0, "N°5": 850.0}

st.title("🏇 PMU Pro Suite & Revenue Hub")
st.sidebar.header("📚 Espace Auteur & Formations")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")
st.sidebar.markdown("""<div class="pub-sidebar">🎯 <b>PUBLICITÉ PARTENAIRE</b><br><small>Formations certifiées en électricité résidentielle et solaire.</small></div>""", unsafe_allow_html=True)

nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique")
t_simple = st.sidebar.slider("Taxe Jeu Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur", "🧮 Stratégies", "🏆 Combinés"])
with onglet1:
    for cheval in list(st.session_state.mises.keys()):
        st.session_state.mises[cheval] = st.slider(f"Mise totale sur le {cheval}", 50, 50000, int(st.session_state.mises[cheval]), 50)
    cotes_s = calculer_jeu_simple(st.session_state.mises, t_simple)
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
    st.bar_chart(data=df_mises, x="Cheval", y="Mises (€)", color="#0284c7")
    df_rep = pd.DataFrame({"Partant": list(cotes_s.keys()), "Mises (€)": list(st.session_state.mises.values()), "Cote": [f"{v:.2f} X" for v in cotes_s.values()]})
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
    pari_simule = st.number_input("Montant de votre pari (€) :", min_value=0.0, value=500.0, step=50.0)
    if pari_simule > 0:
        c_avant = cotes_s[cible]
        m_copie = st.session_state.mises.copy()
        m_copie[cible] += pari_simule
        c_apres = calculer_jeu_simple(m_copie, t_simple)[cible]
        st.warning(f"La cote passera de {c_avant:.2f} à {c_apres:.2f} (-{((c_avant - c_apres) / c_avant) * 100:.1f}%)")

with onglet3:
    c_couples = calculer_couples(st.session_state.mises, t_combine)
    df_cp = pd.DataFrame(list(c_couples.items()), columns=["Duo", "Cote Estimée"])
    st.dataframe(df_cp, use_container_width=True, hide_index=True)
