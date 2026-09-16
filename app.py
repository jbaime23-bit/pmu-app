import streamlit as st
import math
import pandas as pd
import io

st.set_page_config(page_title="Simulateur PMU Pro", page_icon="🏇", layout="wide")

st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

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
    st.text_input("Mot de passe :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

def calculer_cotes(mises_actuelles, taux_prelevement=0.15):
    masse_totale = sum(max(0.0, float(v)) for v in mises_actuelles.values())
    if masse_totale == 0:
        return {k: 99.0 for k in mises_actuelles.keys()}
    masse_net = masse_totale * (1 - taux_prelevement)
    cotes = {}
    for cheval, mise in mises_actuelles.items():
        mise_valide = max(0.0, float(mise))
        if mise_valide > 0:
            cote = math.floor((masse_net / mise_valide) * 100) / 100
            cotes[cheval] = max(cote, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes

if 'mises' not in st.session_state:
    st.session_state.mises = {"Cheval 1": 15000.0, "Cheval 2": 8500.0, "Cheval 3": 4200.0, "Cheval 4": 2100.0, "Cheval 5": 950.0}

st.title("🏇 Plateforme PMU Pro & Analyse d'Enjeux")
if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state.authentifie 
