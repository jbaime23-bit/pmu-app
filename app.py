import streamlit as st
import math
import pandas as pd
import altair as alt

# 1. CONFIGURATION DE LA PAGE & STYLES PRO
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

st.markdown("""<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}
.pub-banner {background-color: #fef08a; border: 2px dashed #ca8a04; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; color: #854d0e; font-weight: bold;}
.pub-sidebar {background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; text-align: center; border-radius: 6px; margin-top: 20px; color: #1e40af;}
</style>""", unsafe_allow_html=True)

# 2. SYSTÈME DE SÉCURITÉ (MOT DE PASSE)
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

# 3. INITIALISATION DURABLE DES MISES
if 'mises' not in st.session_state:
    st.session_state.mises = {"N°1": 12000.0, "N°2": 8000.0, "N°3": 4500.0, "N°4": 2000.0, "N°5": 850.0}

# 4. BARRE LATÉRALE : ESPACE AUTEUR & RÉGLAGES DYNAMIQUES
st.sidebar.header("📚 Espace Auteur & Pro")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")

# Fonctionnalité 1 : Administration des Publicités en direct
st.sidebar.markdown("---")
st.sidebar.header("📢 Gestion des Publicités")
texte_pub_principal = st.sidebar.text_area("Bannière supérieure :", value="📢 ESPACE PUBLICITAIRE DISPONIBLE - Louez cet encart pour booster votre visibilité !")
texte_pub_sidebar = st.sidebar.text_input("Texte pub latérale :", value="Formations certifiées en électricité.")

# Affichage des bannières publicitaires personnalisables
st.markdown(f"""<div class="pub-banner">{texte_pub_principal}</div>""", unsafe_allow_html=True)
st.sidebar.markdown(f"""<div class="pub-sidebar">🎯 <b>PARTENAIRE</b><br><small>{texte_pub_sidebar}</small></div>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Paramètres Course")
nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique")
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

# Fonctionnalité 2 : Bouton de simulation de Flux API Direct en direct
if st.sidebar.button("🔄 Synchroniser Enjeux Réels (Live)"):
    st.session_state.mises = {"N°1": 24500.0, "N°2": 18200.0, "N°3": 9100.0, "N°4": 4300.0, "N°5": 1150.0}
    st.sidebar.success("Données de la course synchronisées !")

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

# 5. FONCTIONS DE CALCUL DU PARI MUTUEL EN DIRECT
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(max(0.0, float(v)) for v in mises.values())
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    cotes = {}
    for cheval, mise in mises.items():
        if mise > 0:
            cotes[cheval] = max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10)
        else: cotes[cheval] = 99.0
    return cotes, masse_totale

def calculer_paris_complexes(mises, taux_comb):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0: return {}, {}, {}, {}
    masse_net = masse_totale * (1 - taux_comb)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    c_couples, c_tierce, c_quarte, c_quinte = {}, {}, {}, {}
    chevaux = list(mises.keys())
    
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p_comb = (probabilites[c1]*probabilites[c2]) * 2
            if p_comb > 0: c_couples[f"{c1} - {c2}"] = max(math.floor((masse_net / (masse_net * p_comb * 0.4)) * 100) / 100, 2.0)
            
            for k in range(j + 1, len(chevaux)):
                c3 = chevaux[k]
                p_t = probabilites[c1]*probabilites[c2]*probabilites[c3]*6
                if p_t > 0: c_tierce[f"{c1}-{c2}-{c3}"] = max(math.floor((masse_net / (masse_net * p_t * 0.2)) * 100) / 100, 5.0)
                
                for l in range(k + 1, len(chevaux)):
                    c4 = chevaux[l]
                    p_q = probabilites[c1]*probabilites[c2]*probabilites[c3]*probabilites[c4]*24
                    if p_q > 0: c_quarte[f"{c1}-{c2}-{c3}-{c4}"] = max(math.floor((masse_net / (masse_net * p_q * 0.1)) * 100) / 100, 10.0)
                    
                    for m in range(l + 1, len(chevaux)):
                        c5 = chevaux[m]
                        p_qi = probabilites[c1]*probabilites[c2]*probabilites[c3]*probabilites[c4]*probabilites[c5]*120
                        if p_qi > 0: c_quinte[f"{c1}-{c2}-{c3}-{c4}-{c5}"] = max(math.floor((masse_net / (masse_net * p_qi * 0.05)) * 100) / 100, 20.0)
    return c_couples, c_tierce, c_quarte, c_quinte

# 6. GESTION DE L'AFFICHAGE ET DES ENJEUX
st.title("🏇 PMU Pro Suite Ultimate Hub")

onglet1, onglet2, onglet3 = st.tabs(["📊 Calculateur & Graphiques", "🧮 Stratégies Avancées", "🏆 Paris Multiples (Tiercé/Quarté/Quinté)"])

with onglet1:
    st.header(f"Analyse en direct : {nom_course}")
    col_sliders, col_visuals = st.columns([1, 1.3])
    with col_sliders:
        st.subheader("Ajuster les Enjeux Manuels")
        for ch in list(st.session_state.mises.keys()):
            st.session_state.mises[ch] = st.slider(f"Mise totale sur le {ch} (€)", 50, 50000, int(st.session_state.mises[ch]), 50)
            
    cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
    
    with col_visuals:
        # Fonctionnalité 3 : Graphique Avancé (Diagramme en secteurs / Donut)
        st.subheader("Répartition des Parts de Marché Financières")
        chart = alt.Chart(df_mises).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Mises (€)", type="quantitative"),
            color=alt.Color(field="Cheval", type="nominal"),
            tooltip=["Cheval", "Mises (€)"]
        )
        st.altair_chart(chart, use_container_width=True)
        
    st.subheader("📋 Tableau Directeur des Cotes Directes")
    df_rep = pd.DataFrame({"Partant": list(cotes_s.keys()), "Mises Déposées (€)": list(st.session_state.mises.values()), "Cote Officielle": [f"{v:.2f} X" for v in cotes_s.values()]})
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outil d'Arbitrage Spéculatif")
    cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
    pari_simule = st.number_input("Montant de votre pari (€) :", min_value=0.0, value=500.0, step=50.0)
    if pari_simule > 0:
        c_avant = cotes_s[cible]
        m_copie = st.session_state.mises.copy()
        m_copie[cible] += pari_simule
        c_apres = calculer_jeu_simple(m_copie, t_simple)[cible]
        st.warning(f"La cote passera de {c_avant:.2f} à {c_apres:.2f} (-{((c_avant - c_apres) / c_avant) * 100:.1f}%)")

with onglet3:
    st.header("🏆 Moteur Prédictif de Paris Combinés")
    c_cp, c_t, c_qa, c_qi = calculer_paris_complexes(st.session_state.mises, t_combine)
    
    sel_mode = st.selectbox("Sélectionner la catégorie de pari combiné :", ["Couplé", "Tiercé", "Quarté", "Quinté"])
    if sel_mode == "Couplé":
        st.dataframe(pd.DataFrame(list(c_cp.items()), columns=["Duo", "Cote"]), use_container_width=True, hide_index=True)
    elif sel_mode == "Tiercé":
        st.dataframe(pd.DataFrame(list(c_t.items()), columns=["Trio", "Cote"]), use_container_width=True, hide_index=True)
    elif sel_mode == "Quarté":
        st.dataframe(pd.DataFrame(list(c_qa.items()), columns=["Quatuor", "Cote"]), use_container_width=True, hide_index=True)
    elif sel_mode == "Quinté":
        st.dataframe(pd.DataFrame(list(c_qi.items()), columns=["Quintette", "Cote"]), use_container_width=True, hide_index=True)
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
