import streamlit as st
import math
import pandas as pd
import io

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

st.markdown("""<div class="pub-banner">📢 ESPACE PUBLICITAIRE DISPONIBLE<br><span style="font-size: 0.85em; font-weight: normal;">Boostez vos paris ou promouvez vos services ici ! Contactez l'administrateur pour louer cet espace.</span></div>""", unsafe_allow_html=True)

def calculer_jeu_simple(mises, taux=0.15):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0:
        return {k: 99.0 for k in mises.keys()}, 0.0, 0.0
    masse_net = masse_totale * (1 - taux)
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cote = math.floor((masse_net / mise) * 100) / 100
            cotes[cheval] = max(cote, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes, masse_totale, masse_net

def calculer_couples_et_tierce(mises, taux_combines=0.18):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0:
        return {}, {}
    masse_net = masse_totale * (1 - taux_combines)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    cotes_couples, cotes_tierce = {}, {}
    chevaux = list(mises.keys())
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p1, p2 = probabilites[c1], probabilites[c2]
            if p1 > 0 and p2 > 0:
                p_comb = (p1 * (p2 / max(0.01, 1 - p1))) + (p2 * (p1 / max(0.01, 1 - p2)))
                cote = math.floor((masse_net / max(1.0, masse_net * p_comb * 0.4)) * 100) / 100
                cotes_couples[f"{c1} - {c2}"] = max(cote, 2.0)
    return cotes_couples, cotes_tierce

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
    cotes_s, m_totale, m_net = calculer_jeu_simple(st.session_state.mises, t_simple)
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
    c_couples, _ = calculer_couples_et_tierce(st.session_state.mises, t_combine)
    df_cp = pd.DataFrame(list(c_couples.items()), columns=["Duo", "Cote Estimée"])
    st.dataframe(df_cp, use_container_width=True, hide_index=True)import streamlit as st
import math
import pandas as pd
import io

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="PMU Pro Suite & Éducation", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {background-color: #f8fafc;}
    .pub-banner {
        background-color: #fef08a;
        border: 2px dashed #ca8a04;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #854d0e;
        font-weight: bold;
    }
    .pub-sidebar {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 10px;
        text-align: center;
        border-radius: 6px;
        margin-top: 20px;
        color: #1e40af;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SYSTÈME DE MOT DE PASSE SÉCURISÉ
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
    st.write("Veuillez saisir votre clé d'accès pour déverrouiller les algorithmes.")
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

# 3. BANNIÈRE PUBLICITAIRE HAUT DE PAGE
st.markdown("""
    <div class="pub-banner">
        📢 ESPACE PUBLICITAIRE DISPONIBLE<br>
        <span style="font-size: 0.85em; font-weight: normal;">
            Boostez vos paris ou promouvez vos services ici ! Contactez l'administrateur pour louer cet espace.
        </span>
    </div>
    """, unsafe_allow_html=True)

# 4. FONCTIONS DE CALCUL DU PARI MUTUEL
def calculer_jeu_simple(mises, taux=0.15):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0:
        return {k: 99.0 for k in mises.keys()}, 0.0, 0.0
    masse_net = masse_totale * (1 - taux)
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cote = math.floor((masse_net / mise) * 100) / 100
            cotes[cheval] = max(cote, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes, masse_totale, masse_net

def calculer_couples_et_tierce(mises, taux_combines=0.18):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0:
        return {}, {}
    masse_net = masse_totale * (1 - taux_combines)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    cotes_couples = {}
    cotes_tierce = {}
    chevaux = list(mises.keys())
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p1, p2 = probabilites[c1], probabilites[c2]
            if p1 > 0 and p2 > 0:
                p_comb = (p1 * (p2 / max(0.01, 1 - p1))) + (p2 * (p1 / max(0.01, 1 - p2)))
                cote = math.floor((masse_net / max(1.0, masse_net * p_comb * 0.4)) * 100) / 100
                cotes_couples[f"{c1} - {c2}"] = max(cote, 2.0)
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            for k in range(j + 1, len(chevaux)):
                c1, c2, c3 = chevaux[i], chevaux[j], chevaux[k]
                p_tierce = probabilites[c1] * probabilites[c2] * probabilites[c3] * 6
                if p_tierce > 0:
                    cote_t = math.floor((masse_net / max(1.0, masse_net * p_tierce * 0.2)) * 100) / 100
                    cotes_tierce[f"{c1}-{c2}-{c3}"] = max(cote_t, 5.0)
    return cotes_couples, cotes_tierce

# 5. INITIALISATION DES DONNÉES
if 'mises' not in st.session_state:
    st.session_state.mises = {"N°1": 12000.0, "N°2": 8000.0, "N°3": 4500.0, "N°4": 2000.0, "N°5": 850.0}

st.title("🏇 PMU Pro Suite & Revenue Hub")

# 6. BARRE LATÉRALE AVEC PUBLICITÉ 2
st.sidebar.header("📚 Espace Auteur & Formations")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")
st.sidebar.markdown("[🔗 Obtenir votre Certificat de Lecture](https://google.com)") 
st.sidebar.markdown("[🛒 Acheter le guide complet](https://amazon.com)")

st.sidebar.markdown("""
    <div class="pub-sidebar">
        🎯 <b>PUBLICITÉ PARTENAIRE</b><br>
        <small>Formations certifiées en électricité résidentielle et solaire.</small><br>
        <a href="https://google.com" target="_blank" style="color:#2563eb; font-weight:bold; text-decoration:none;">En savoir plus →</a>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique - R1C3")
t_simple = st.sidebar.slider("Taxe Jeu Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

# 7. STRUCTURE DE L'INTERFACE EN ONGLETS
onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Graphiques", "🧮 Outils Stratégiques", "🏆 Paris Combinés (Couplé/Tiercé)"])

with onglet1:
    st.header(f"Analyse des masses : {nom_course}")
    col_g, col_d = st.columns([1, 1.5])
    with col_g:
        st.subheader("Ajuster les Enjeux (€)")
        for cheval in list(st.session_state.mises.keys()):
            st.session_state.mises[cheval] = st.slider(f"Mise totale sur le {cheval}", 50, 50000, int(st.session_state.mises[cheval]), 50)
    cotes_s, m_totale, m_net = calculer_jeu_simple(st.session_state.mises, t_simple)
    with col_d:
        st.subheader("Visualisation du Pool Financier")
        df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
        st.bar_chart(data=df_mises, x="Cheval", y="Mises (€)", color="#0284c7")
    st.subheader("📋 Rapports Probables Directs")
    df_rep = pd.DataFrame({"Partant": list(cotes_s.keys()), "Mises Déposées (€)": list(st.session_state.mises.values()), "Cote Officielle": [f"{v:.2f} X" for v in cotes_s.values()]})
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outils d'Aide à la Décision Spéculative")
    col_imp, col_dutch = st.columns(2)
    with col_imp:
        st.subheader("📉 Simulateur de Chute de Cote")
        cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
        pari_simule = st.number_input("Montant de votre pari (€) :", min_value=0.0, value=500.0, step=50.0)
        if pari_simule > 0:
            c_avant = cotes_s[cible]
            m_copie = st.session_state.mises.copy()
            m_copie[cible] += pari_simule
            c_apres = calculer_jeu_simple(m_copie, t_simple)[cible]
            chute = ((c_avant - c_apres) / c_avant) * 100
            st.warning(f"La cote passera de {c_avant:.2f} à {c_apres:.2f} (-{chute:.1f}%)")
    with col_dutch:
        st.subheader("🛡️ Répartiteur Anti-Perte (Dutching)")
        selection = st.multiselect("Sélectionnez vos favoris :", list(st.session_state.mises.keys()), default=list(st.session_state.mises.keys())[:2])
        budget = st.number_input("Votre budget total de couverture (€) :", min_value=1.0, value=100.0)
        if selection and budget > 0:
            sub_cotes = {c: cotes_s[c] for c in selection}
            inverses = sum(1/c for c in sub_cotes.values())
            rendement = (1 / inverses) * 100
            st.write(f"Rendement de couverture : **{rendement:.1f}%**")
            for ch, cot in sub_cotes.items():
                m_exacte = (budget * (1/cot)) / inverses
                st.info(f"👉 **{ch}** : Misez **{m_exacte:.2f}€**")

with onglet3:
    st.header("🏆 Rapports Estimés des Paris Multiples")
    c_couples, c_tierce = calculer_couples_et_tierce(st.session_state.mises, t_combine)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👫 Combinaisons Couplé Gagnant")
        df_cp = pd.DataFrame(list(c_couples.items()), columns=["Duo", "Cote Estimée"])
        st.dataframe(df_cp, use_container_width=True, hide_index=True)
    with c2:
        st.subheader("🎓 Combinaisons Tiercé")
        df_tc = pd.DataFrame(list(c_tierce.items()), columns=["Trio", "Cote Estimée"])
        st.dataframe(df_tc, use_container_width=True, hide_index=True)

# 8. EXPORTATION EXCEL
st.markdown("---")
st.subheader("💾 Exportation des données")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_rep.to_excel(writer, index=False)

st.download_button(label="📥 Télécharger import streamlit as st
import math
import pandas as pd
import io

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="PMU Pro Suite & Éducation", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {background-color: #f8fafc;}
    .pub-banner {
        background-color: #fef08a;
        border: 2px dashed #ca8a04;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #854d0e;
        font-weight: bold;
    }
    .pub-sidebar {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 10px;
        text-align: center;
        border-radius: 6px;
        margin-top: 20px;
        color: #1e40af;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SYSTÈME DE MOT DE PASSE SÉCURISÉ
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
    st.write("Veuillez saisir votre clé d'accès pour déverrouiller les algorithmes.")
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

# 3. BANNIÈRE PUBLICITAIRE HAUT DE PAGE
st.markdown("""
    <div class="pub-banner">
        📢 ESPACE PUBLICITAIRE DISPONIBLE<br>
        <span style="font-size: 0.85em; font-weight: normal;">
            Boostez vos paris ou promouvez vos services ici ! Contactez l'administrateur pour louer cet espace.
        </span>
    </div>
    """, unsafe_allow_html=True)

# 4. FONCTIONS DE CALCUL DU PARI MUTUEL
def calculer_jeu_simple(mises, taux=0.15):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0:
        return {k: 99.0 for k in mises.keys()}, 0.0, 0.0
    masse_net = masse_totale * (1 - taux)
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cote = math.floor((masse_net / mise) * 100) / 100
            cotes[cheval] = max(cote, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes, masse_totale, masse_net

def calculer_couples_et_tierce(mises, taux_combines=0.18):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0:
        return {}, {}
    masse_net = masse_totale * (1 - taux_combines)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    cotes_couples = {}
    cotes_tierce = {}
    chevaux = list(mises.keys())
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p1, p2 = probabilites[c1], probabilites[c2]
            if p1 > 0 and p2 > 0:
                p_comb = (p1 * (p2 / max(0.01, 1 - p1))) + (p2 * (p1 / max(0.01, 1 - p2)))
                cote = math.floor((masse_net / max(1.0, masse_net * p_comb * 0.4)) * 100) / 100
                cotes_couples[f"{c1} - {c2}"] = max(cote, 2.0)
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            for k in range(j + 1, len(chevaux)):
                c1, c2, c3 = chevaux[i], chevaux[j], chevaux[k]
                p_tierce = probabilites[c1] * probabilites[c2] * probabilites[c3] * 6
                if p_tierce > 0:
                    cote_t = math.floor((masse_net / max(1.0, masse_net * p_tierce * 0.2)) * 100) / 100
                    cotes_tierce[f"{c1}-{c2}-{c3}"] = max(cote_t, 5.0)
    return cotes_couples, cotes_tierce

# 5. INITIALISATION DES DONNÉES
if 'mises' not in st.session_state:
    st.session_state.mises = {"N°1": 12000.0, "N°2": 8000.0, "N°3": 4500.0, "N°4": 2000.0, "N°5": 850.0}

st.title("🏇 PMU Pro Suite & Revenue Hub")

# 6. BARRE LATÉRALE AVEC PUBLICITÉ 2
st.sidebar.header("📚 Espace Auteur & Formations")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")
st.sidebar.markdown("[🔗 Obtenir votre Certificat de Lecture](https://google.com)") 
st.sidebar.markdown("[🛒 Acheter le guide complet](https://amazon.com)")

st.sidebar.markdown("""
    <div class="pub-sidebar">
        🎯 <b>PUBLICITÉ PARTENAIRE</b><br>
        <small>Formations certifiées en électricité résidentielle et solaire.</small><br>
        <a href="https://google.com" target="_blank" style="color:#2563eb; font-weight:bold; text-decoration:none;">En savoir plus →</a>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique - R1C3")
t_simple = st.sidebar.slider("Taxe Jeu Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

# 7. STRUCTURE DE L'INTERFACE EN ONGLETS
onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Graphiques", "🧮 Outils Stratégiques", "🏆 Paris Combinés (Couplé/Tiercé)"])

with onglet1:
    st.header(f"Analyse des masses : {nom_course}")
    col_g, col_d = st.columns([1, 1.5])
    with col_g:
        st.subheader("Ajuster les Enjeux (€)")
        for cheval in list(st.session_state.mises.keys()):
            st.session_state.mises[cheval] = st.slider(f"Mise totale sur le {cheval}", 50, 50000, int(st.session_state.mises[cheval]), 50)
    cotes_s, m_totale, m_net = calculer_jeu_simple(st.session_state.mises, t_simple)
    with col_d:
        st.subheader("Visualisation du Pool Financier")
        df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
        st.bar_chart(data=df_mises, x="Cheval", y="Mises (€)", color="#0284c7")
    st.subheader("📋 Rapports Probables Directs")
    df_rep = pd.DataFrame({"Partant": list(cotes_s.keys()), "Mises Déposées (€)": list(st.session_state.mises.values()), "Cote Officielle": [f"{v:.2f} X" for v in cotes_s.values()]})
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outils d'Aide à la Décision Spéculative")
    col_imp, col_dutch = st.columns(2)
    with col_imp:
        st.subheader("📉 Simulateur de Chute de Cote")
        cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
        pari_simule = st.number_input("Montant de votre pari (€) :", min_value=0.0, value=500.0, step=50.0)
        if pari_simule > 0:
            c_avant = cotes_s[cible]
            m_copie = st.session_state.mises.copy()
            m_copie[cible] += pari_simule
            c_apres = calculer_jeu_simple(m_copie, t_simple)[cible]
            chute = ((c_avant - c_apres) / c_avant) * 100
            st.warning(f"La cote passera de {c_avant:.2f} à {c_apres:.2f} (-{chute:.1f}%)")
    with col_dutch:
        st.subheader("🛡️ Répartiteur Anti-Perte (Dutching)")
        selection = st.multiselect("Sélectionnez vos favoris :", list(st.session_state.mises.keys()), default=list(st.session_state.mises.keys())[:2])
        budget = st.number_input("Votre budget total de couverture (€) :", min_value=1.0, value=100.0)
        if selection and budget > 0:
            sub_cotes = {c: cotes_s[c] for c in selection}
            inverses = sum(1/c for c in sub_cotes.values())
            rendement = (1 / inverses) * 100
            st.write(f"Rendement de couverture : **{rendement:.1f}%**")
            for ch, cot in sub_cotes.items():
                m_exacte = (budget * (1/cot)) / inverses
                st.info(f"👉 **{ch}** : Misez **{m_exacte:.2f}€**")

with onglet3:
    st.header("🏆 Rapports Estimés des Paris Multiples")
    c_couples, c_tierce = calculer_couples_et_tierce(st.session_state.mises, t_combine)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👫 Combinaisons Couplé Gagnant")
        df_cp = pd.DataFrame(list(c_couples.items()), columns=["Duo", "Cote Estimée"])
        st.dataframe(df_cp, use_container_width=True, hide_index=True)
    with c2:
        st.subheader("🎓 Combinaisons Tiercé")
        df_tc = pd.DataFrame(list(c_tierce.items()), columns=["Trio", "Cote Estimée"])
        st.dataframe(df_tc, use_container_width=True, hide_index=True)

# 8. EXPORTATION EXCEL
st.markdown("---")
st.subheader("💾 Exportation des données")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_rep.to_excel(writer, index=False)

st.download_button(label="📥 Téléchargersreamlit as st
import math
import pandas as pd
import io

st.set_page_config(page_title="PMU Pro Suite & Éducation", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {background-color: #f8fafc;}
    .pub-banner {
        background-color: #fef08a;
        border: 2px dashed #ca8a04;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #854d0e;
        font-weight: bold;
    }
    .pub-sidebar {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 10px;
        text-align: center;
        border-radius: 6px;
        margin-top: 20px;
        color: #1e40af;
    }
    </style>
    """, unsafe_allow_html=True)

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
    st.write("Veuillez saisir votre clé d'accès pour déverrouiller les algorithmes.")
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

st.markdown("""
    <div class="pub-banner">
        📢 ESPACE PUBLICITAIRE DISPONIBLE<br>
        <span style="font-size: 0.85em; font-weight: normal;">
            Boostez vos paris ou promouvez vos services ici ! Contactez l'administrateur pour louer cet espace.
        </span>
    </div>
    """, unsafe_allow_html=True)

def calculer_jeu_simple(mises, taux=0.15):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0:
        return {k: 99.0 for k in mises.keys()}, 0.0, 0.0
    masse_net = masse_totale * (1 - taux)
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cote = math.floor((masse_net / mise) * 100) / 100
            cotes[cheval] = max(cote, 1.10)
        else:
            cotes[cheval] = 99.0
    return cotes, masse_totale, masse_net

def calculer_couples_et_tierce(mises, taux_combines=0.18):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0:
        return {}, {}
    masse_net = masse_totale * (1 - taux_combines)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    cotes_couples = {}
    cotes_tierce = {}
    chevaux = list(mises.keys())
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p1, p2 = probabilites[c1], probabilites[c2]
            if p1 > 0 and p2 > 0:
                p_comb = (p1 * (p2 / max(0.01, 1 - p1))) + (p2 * (p1 / max(0.01, 1 - p2)))
                cote = math.floor((masse_net / max(1.0, masse_net * p_comb * 0.4)) * 100) / 100
                cotes_couples[f"{c1} - {c2}"] = max(cote, 2.0)
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            for k in range(j + 1, len(chevaux)):
                c1, c2, c3 = chevaux[i], chevaux[j], chevaux[k]
                p_tierce = probabilites[c1] * probabilites[c2] * probabilites[c3] * 6
                if p_tierce > 0:
                    cote_t = math.floor((masse_net / max(1.0, masse_net * p_tierce * 0.2)) * 100) / 100
                    cotes_tierce[f"{c1}-{c2}-{c3}"] = max(cote_t, 5.0)
    return cotes_couples, cotes_tierce

st.title("🏇 PMU Pro Suite & Revenue Hub")

if 'mises' not in st.session_state:
    st.session_state.mises = {"N°1": 12000.0, "N°2": 8000.0, "N°3": 4500.0, "N°4": 2000.0, "N°5": 850.0}

st.sidebar.header("📚 Espace Auteur & Formations")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")
st.sidebar.markdown("[🔗 Obtenir votre Certificat de Lecture](https://google.com)") 
st.sidebar.markdown("[🛒 Acheter le guide complet](https://amazon.com)")

st.sidebar.markdown("""
    <div class="pub-sidebar">
        🎯 <b>PUBLICITÉ PARTENAIRE</b><br>
        <small>Formations certifiées en électricité résidentielle et solaire.</small><br>
        <a href="https://google.com" target="_blank" style="color:#2563eb; font-weight:bold; text-decoration:none;">En savoir plus →</a>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique - R1C3")
t_simple = st.sidebar.slider("Taxe Jeu Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Graphiques", "🧮 Outils Stratégiques", "🏆 Paris Combinés (Couplé/Tiercé)"])

with onglet1:
    st.header(f"Analyse des masses : {nom_course}")
    col_g, col_d = st.columns([1, 1.5])
    with col_g:
        st.subheader("Ajuster les Enjeux (€)")
        for cheval in list(st.session_state.mises.keys()):
            st.session_state.mises[cheval] = st.slider(f"Mise totale sur le {cheval}", 50, 50000, int(st.session_state.mises[cheval]), 50)
    cotes_s, m_totale, m_net = calculer_jeu_simple(st.session_state.mises, t_simple)
    with col_d:
        st.subheader("Visualisation du Pool Financier")
        df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
        st.bar_chart(data=df_mises, x="Cheval", y="Mises (€)", color="#0284c7")
    st.subheader("📋 Rapports Probables Directs")
    df_rep = pd.DataFrame({"Partant": list(cotes_s.keys()), "Mises Déposées (€)": list(st.session_state.mises.values()), "Cote Officielle": [f"{v:.2f} X" for v in cotes_s.values()]})
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outils d'Aide à la Décision Spéculative")
    col_imp, col_dutch = st.columns(2)
    with col_imp:
        st.subheader("📉 Simulateur de Chute de Cote")
        cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
        pari_simule = st.number_input("Montant de votre pari (€) :", min_value=0.0, value=500.0, step=50.0)
        if pari_simule > 0:
            c_avant = cotes_s[cible]
            m_copie = st.session_state.mises.copy()
            m_copie[cible] += pari_simule
            c_apres = calculer_jeu_simple(m_copie, t_simple)[cible]
            chute = ((c_avant - c_apres) / c_avant) * 100
            st.warning(f"La cote passera de {c_avant:.2f} à {c_apres:.2f} (-{chute:.1f}%)")
    with col_dutch:
        st.subheader("🛡️ Répartiteur Anti-Perte (Dutching)")
        selection = st.multiselect("Sélectionnez vos favoris :", list(st.session_state.mises.keys()), default=list(st.session_state.mises.keys())[:2])
        budget = st.number_input("Votre budget total de couverture (€) :", min_value=1.0, value=100.0)
        if selection and budget > 0:
            sub_cotes = {c: cotes_s[c] for c in selection}
            inverses = sum(1/c for c in sub_cotes.values())
            rendement = (1 / inverses) * 100
            st.write(f"Rendement de couverture : **{rendement:.1f}%**")
            for ch, cot in sub_cotes.items():
                m_exacte = (budget * (1/cot)) / inverses
                st.info(f"👉 **{ch}** : Misez **{m_exacte:.2f}€**")

with onglet3:
    st.header("🏆 Rapports Estimés des Paris Multiples")
    c_couples, c_tierce = calculer_couples_et_tierce(st.session_state.mises, t_combine)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👫 Combinaisons Couplé Gagnant")
        df_cp = pd.DataFrame(list(c_couples.items()), columns=["Duo", "Cote Estimée"])
        st.dataframe(df_cp, use_container_width=True, hide_index=True)
    with c2:
        st.subheader("🎓 Combinaisons Tiercé")
        df_tc = pd.DataFrame(list(c_tierce.items()), columns=["Trio", "Cote Estimée"])
        st.dataframe(df_tc, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("💾 Exportation des données")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_rep.to_excel(writer, index=False, sheet_name='Jeu_Simple')
    pd.DataFrame(list(c_couples.items()), columns=["Duo", "Cote"]).to_excel(writer, index=False, sheet_name='Couples')

st.download_button(label="📥 Télécharger import streamlit as st
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
