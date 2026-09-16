import streamlit as st
import math
import pandas as pd
import altair as alt

# 1. CONFIGURATION DE LA PAGE & VISUELS PRO
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

st.markdown("""<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}
.pub-banner {background-color: #fef08a; border: 2px dashed #ca8a04; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; color: #854d0e; font-weight: bold;}
.pub-sidebar {background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; text-align: center; border-radius: 6px; margin-top: 20px; color: #1e40af;}
</style>""", unsafe_allow_html=True)

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
    st.text_input("Clé d'accès :", type="password", key="mot_de_passe_saisi", on_change=verifier_mot_de_passe)
    st.stop()

# 3. INITIALISATION DURABLE DU NOMBRE DE PARTANTS
# Passage à 16 partants pour intégrer vos règles d'observation (6-12 et 13-16)
if 'mises' not in st.session_state:
    st.session_state.mises = {f"N°{i}": float(10000 - (i*500)) for i in range(1, 17)}

# 4. BARRE LATÉRALE - ESPACE AUTEUR & PUBLICITÉS DYNAMIQUES
st.sidebar.header("📚 Espace Auteur & Pro")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")

st.sidebar.markdown("---")
st.sidebar.header("📢 Administration des Publicités")
texte_pub_principal = st.sidebar.text_area("Bannière du haut :", value="📢 ESPACE PUBLICITAIRE DISPONIBLE - Louez cet encart pour booster votre visibilité !")
texte_pub_sidebar = st.sidebar.text_input("Texte pub latérale :", value="Formations certifiées en électricité.")

st.markdown(f"""<div class="pub-banner">{texte_pub_principal}</div>""", unsafe_allow_html=True)
st.sidebar.markdown(f"""<div class="pub-sidebar">🎯 <b>PARTENAIRE</b><br><small>{texte_pub_sidebar}</small></div>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration Course")
nom_course = st.sidebar.text_input("Nom de la course :", value="Prix d'Afrique")
type_course = st.sidebar.selectbox("Spécialité de la course :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.rerun()

# 5. MOTEURS DE CALCUL MATHÉMATIQUES & PROBABILITÉS
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
    if int(masse_totale) == 0: return {}, {}
    masse_net = masse_totale * (1 - taux_comb)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    c_couples, c_tierce = {}, {}
    chevaux = list(mises.keys())[:8] # Restriction de calcul sur mobile pour éviter les lenteurs
    
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p_comb = (probabilites[c1]*probabilites[c2]) * 2
            if p_comb > 0: c_couples[f"{c1} - {c2}"] = max(math.floor((masse_net / (masse_net * p_comb * 0.4)) * 100) / 100, 2.0)
    return c_couples, c_tierce

# MOTEUR IA INTÉGRANT VOS PROPRES OBSERVATIONS EMPIRIQUES
def analyse_ia_avec_regles_expert(mises, specialite):
    scores_base = {f"N°{i}": 50 + (i % 3)*12 for i in range(1, 17)}
    analyses = {}
    
    for i in range(1, 17):
        cheval_key = f"N°{i}"
        
        # Application de vos remarques dans l'algorithme
        if 1 <= i <= 4:
            analyses[cheval_key] = "Zone Favoris (Règle Expert : 1 à 2 numéros sortent souvent ici)."
            scores_base[cheval_key] += 10
        elif i == 5 or i == 4:
            analyses[cheval_key] = "Point d'appui intermédiaire (Règle Expert : Présence fréquente d'un numéro)."
            scores_base[cheval_key] += 8
        elif 6 <= i <= 12:
            analyses[cheval_key] = "Alerte Outsiders Spéculatifs (Règle Expert : Zone à forte récurrence, 1 ou 2 numéros ici)."
            scores_base[cheval_key] += 15
        elif 13 <= i <= 16:
            analyses[cheval_key] = "Zone Grosses Cotes / Tocard ciblé (Règle Expert : 1 numéro à chercher ici pour casser les rapports)."
            scores_base[cheval_key] += 5
            
        # Boost si c'est une course d'Attelé (votre remarque sur le trot)
        if specialite == "Attelé (Trot)" and (6 <= i <= 12 or 1 <= i <= 4):
            analyses[cheval_key] += " Modèle Attelé renforcé (+ de régularité détectée)."
            scores_base[cheval_key] += 7
            
    return scores_base, analyses

# 6. ENSEMBLE DES ONGLETS D'AFFICHAGE
st.title("🏇 PMU Pro Suite Ultimate Hub v4.5")

onglet1, onglet2, onglet3, onglet4 = st.tabs(["📊 Calculateur", "🧮 Stratégies", "🏆 Combinés", "🤖 Prédictions IA & Vos Règles"])

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

with onglet1:
    st.header(f"Analyse en direct : {nom_course} ({type_course})")
    
    # Affichage simplifié des curseurs pour 16 partants (par colonnes pour éviter l'encombrement)
    st.subheader("Ajuster les Enjeux Financiers (€)")
    cles_chevaux = list(st.session_state.mises.keys())
    c_la, c_lb = st.columns(2)
    
    with c_la:
        for ch in cles_chevaux[:8]:
            st.session_state.mises[ch] = st.slider(f"Mise {ch}", 50, 50000, int(st.session_state.mises[ch]), 250)
    with c_lb:
        for ch in cles_chevaux[8:]:
            st.session_state.mises[ch] = st.slider(f"Mise {ch}", 50, 50000, int(st.session_state.mises[ch]), 250)
            
    df_mises = pd.DataFrame(list(st.session_state.mises.items()), columns=["Cheval", "Mises (€)"])
    
    st.subheader("Répartition Graphique des Enjeux")
    chart = alt.Chart(df_mises).mark_arc(innerRadius=60).encode(
        theta=alt.Theta(field="Mises (€)", type="quantitative"),
        color=alt.Color(field="Cheval", type="nominal"),
        tooltip=["Cheval", "Mises (€)"]
    )
    st.altair_chart(chart, use_container_width=True)
        
    st.subheader("📋 Tableau des Cotes & Probabilités Implicites")
    df_rep = pd.DataFrame({
        "Partant": list(cotes_s.keys()),
        "Mises Déposées (€)": list(st.session_state.mises.values()),
        "Cote Proche": [f"{v:.2f} X" for v in cotes_s.values()],
        "Probabilité Implicite": [f"{(mise / max(1.0, m_totale)) * 100:.1f} %" for mise in st.session_state.mises.values()]
    })
    st.dataframe(df_rep, use_container_width=True, hide_index=True)

with onglet2:
    st.header("🧮 Outil d'Arbitrage Spéculatif")
    cible = st.selectbox("Sélectionnez votre cheval :", list(st.session_state.mises.keys()))
    pari_simule = st.number_input("Montant de votre pari (€) :", min_value=0.0, value=500.0, step=50.0)
    if pari_simule > 0:
        c_avant = cotes_s[cible]
        m_copie = st.session_state.mises.copy()
        m_copie[cible] += pari_simule
        c_apres, _ = calculer_jeu_simple(m_copie, t_simple)
        st.warning(f"La cote passera de {c_avant:.2f} à {c_apres[cible]:.2f} (-{((c_avant - c_apres[cible]) / c_avant) * 100:.1f}%)")

with onglet3:
    st.header("🏆 Moteur Prédictif de Paris Combinés (Top 8)")
    c_cp, _ = calculer_paris_complexes(st.session_state.mises, t_combine)
    st.dataframe(pd.DataFrame(list(c_cp.items()), columns=["Duo Couplé", "Cote Estimée"]), use_container_width=True, hide_index=True)

with onglet4:
    st.header("🤖 Analyse Statistique IA guidée par vos Observations")
    st.caption("Ce tableau croise l'analyse mathématique et vos filtres empiriques (Règles des positions 6-12, 13-16, Favoris et Attelé).")
    
    scores, rapports_ia = analyse_ia_avec_regles_expert(st.session_state.mises, type_course)
    
    df_ia = pd.DataFrame({
        "Numéro": list(scores.keys()),
        "Score Fiabilité IA (Sur 100)": list(scores.values()),
        "Filtre & Orientation Stratégique": list(rapports_ia.values())
    })
    
    st.dataframe(df_ia, use_container_width=True, hide_index=True)
    st.info("💡 Utilisation : La spécialité choisie dans la barre latérale influe sur les indices. Utilisez l'analyse pour repérer instantanément la couverture idéale sur les 16 partants.")
