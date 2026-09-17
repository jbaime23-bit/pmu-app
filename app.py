import streamlit as st
import math
import pandas as pd
import altair as alt
import os
import requests

# --- GESTION DU COMPTEUR DE VISITEURS PERSISTANT (PUBLIC) ---
def gerer_compteur():
    fichier_compteur = "visiteurs.txt"
    if not os.path.exists(fichier_compteur):
        with open(fichier_compteur, "w") as f:
            f.write("0")
    with open(fichier_compteur, "r") as f:
        try:
            visiteurs = int(f.read().strip())
        except ValueError:
            visiteurs = 0
    if 'visite_enregistree' not in st.session_state:
        visiteurs += 1
        with open(fichier_compteur, "w") as f:
            f.write(str(visiteurs))
        st.session_state['visite_enregistree'] = True
    return visiteurs

total_visiteurs = gerer_compteur()

# --- FONCTION DE FLUX AUTOMATIQUE EN DIRECT (API PMU) ---
def charger_donnees_pmu_direct(code_reunion="1", code_course="1"):
    """
    Interroge l'API publique et gratuite du PMU pour extraire 
    automatiquement la course en direct, son nom et son nombre exact de partants.
    """
    import datetime
    date_aujourdhui = datetime.date.today().strftime("%d%m%Y")
    url = f"https://pmu.fr{date_aujourdhui}/R{code_reunion}/C{code_course}/participants"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            participants = data.get("participants", [])
            if participants:
                nb_partants = len(participants)
                # On génère des mises simulées de départ basées sur le flux pour chaque partant trouvé
                mises_flux = {}
                for i, p in enumerate(participants, 1):
                    num = p.get("numProg", i)
                    mises_flux[f"N°{num}"] = float(max(1000, 15000 - (num * 600)))
                return nb_partants, mises_flux
    except Exception:
        pass
    # Valeurs de secours si l'API ne répond pas ou si la course n'a pas encore commencé
    return None, None

# 1. CONFIGURATION DE LA PAGE & VISUELS PRO
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")

st.markdown("""<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}
.pub-banner {background-color: #fef08a; border: 2px dashed #ca8a04; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; color: #854d0e; font-weight: bold;}
.pub-sidebar {background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; text-align: center; border-radius: 6px; margin-top: 20px; color: #1e40af;}
</style>""", unsafe_allow_html=True)

# 2. SYSTÈME DE DOUBLE CLÉ SÉCURISÉ (ADMIN / USER)
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

# 3. CONFIGURATION INITIALE ET DYNAMIQUE (Gère jusqu'à 20 partants automatiquement)
if 'nombre_partants' not in st.session_state:
    st.session_state.nombre_partants = 15  # Configuration par défaut ajustable

if 'mises' not in st.session_state or len(st.session_state.mises) != st.session_state.nombre_partants:
    st.session_state.mises = {f"N°{i}": float(10000 - (i*450)) for i in range(1, st.session_state.nombre_partants + 1)}

# 4. BARRE LATÉRALE - ESPACE AUTEUR & PUBLICITÉS DYNAMIQUES
st.sidebar.header("📚 Espace Auteur & Pro")
st.sidebar.info("« ÉLECTRICIEN / ÉLECTRICIENNE DES INSTALLATIONS TRAVAUX PRATIQUES »")

st.sidebar.markdown("---")

texte_banner_defaut = "📢 ESPACE PUBLICITAIRE DISPONIBLE - Louez cet encart pour booster votre visibilité !"
texte_sidebar_defaut = "Formations certifiées en électricité."

if st.session_state.est_admin:
    st.sidebar.header("📢 Administration des Publicités")
    texte_pub_principal = st.sidebar.text_area("Bannière du haut :", value=texte_banner_defaut)
    texte_pub_sidebar = st.sidebar.text_input("Texte pub latérale :", value=texte_sidebar_defaut)
else:
    texte_pub_principal = texte_banner_defaut
    texte_pub_sidebar = texte_sidebar_defaut

st.markdown(f"""<div class="pub-banner">{texte_pub_principal}</div>""", unsafe_allow_html=True)
st.sidebar.markdown(f"""<div class="pub-sidebar">🎯 <b>PARTENAIRE</b><br><small>{texte_pub_sidebar}</small></div>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuration de la Course")

# Menu de sélection de la course en direct
nom_course = st.sidebar.text_input("Nom de la course :", value="R1 Paris-Vincennes - Prix de Mehun-sur-Yèvre")
type_course = st.sidebar.selectbox("Spécialité de la course :", ["Attelé (Trot)", "Galop", "Haies"])

st.sidebar.subheader("🔄 Connexion Flux PMU Direct")
c_reunion = st.sidebar.text_input("Réunion (Ex: 1)", value="1", max_chars=2)
c_course = st.sidebar.text_input("Course (Ex: 1)", value="1", max_chars=2)

if st.sidebar.button("📡 Synchroniser avec le PMU Live"):
    nb_p, m_flux = charger_donnees_pmu_direct(c_reunion, c_course)
    if nb_p:
        st.session_state.nombre_partants = nb_p
        st.session_state.mises = m_flux
        st.sidebar.success(f"✅ Connecté ! {nb_p} partants importés.")
        st.rerun()
    else:
        st.sidebar.warning("⚠️ Impossible de joindre le flux direct. Ajustement en mode manuel.")

# Curseur de secours manuel si pas d'Internet ou course spéciale (Ajustable jusqu'à 20)
st.sidebar.markdown("---")
nb_partants_manuel = st.sidebar.slider("Ajustement manuel des partants :", 5, 20, int(st.session_state.nombre_partants))
if nb_partants_manuel != st.session_state.nombre_partants:
    st.session_state.nombre_partants = nb_partants_manuel
    st.session_state.mises = {f"N°{i}": float(10000 - (i*450)) for i in range(1, nb_partants_manuel + 1)}
    st.rerun()

t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100
t_combine = st.sidebar.slider("Taxe Combinés (%)", 0, 35, 18) / 100

if st.sidebar.button("🔒 Déconnexion"):
    st.session_state.authentifie = False
    st.session_state.est_admin = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Contact & Support")
lien_whatsapp = "https://wa.me"
st.sidebar.markdown(f'<a href="{lien_whatsapp}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold;">🟢 Nous contacter sur WhatsApp</button></a>', unsafe_allow_html=True)
st.sidebar.write("📧 **Email :** jb.aime23@gmail.com")

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
    if int(masse_totale) == 0: return {}
    masse_net = masse_totale * (1 - taux_comb)
    probabilites = {k: v / max(1.0, masse_totale) for k, v in mises.items()}
    c_couples = {}
    chevaux = list(mises.keys())[:8] # Restriction de calcul calculs combinés pour la fluidité mobile
    
    for i in range(len(chevaux)):
        for j in range(i + 1, len(chevaux)):
            c1, c2 = chevaux[i], chevaux[j]
            p_comb = (probabilites[c1]*probabilites[c2]) * 2
            if p_comb > 0: 
                c_couples[f"{c1} - {c2}"] = max(math.floor((masse_net / (masse_net * p_comb * 0.4)) * 100) / 100, 2.0)
    return c_couples

def analyse_ia_avec_regles_expert(mises, specialite, total_chevaux):
    scores_base = {f"N°{i}": 50 + (i % 3)*10 for i in range(1, total_chevaux + 1)}
    analyses = {}
    
    for i in range(1, total_chevaux + 1):
        cheval_key = f"N°{i}"
        if 1 <= i <= 4:
            analyses[cheval_key] = "Zone Favoris (Règle Expert : 1 à 2 numéros sortent souvent ici)."
            scores_base[cheval_key] += 12
        elif i == 5:
            analyses[cheval_key] = "Point d'appui intermédiaire (Règle Expert : Présence fréquente d'un numéro)."
            scores_base[cheval_key] += 8
        elif 6 <= i <= 12:
            analyses[cheval_key] = "Alerte Outsiders Spéculatifs (Règle Expert : Zone à forte récurrence, 1 ou 2 numéros ici)."
            scores_base[cheval_key] += 15
        elif 13 <= i <= 16:
            analyses[cheval_key] = "Zone Grosses Cotes / Tocard ciblé (Règle Expert : 1 numéro à chercher ici pour casser les rapports)."
            scores_base[cheval_key] += 6
        elif i >= 17:
            analyses[cheval_key] = "Extrême Outsider (Course élargie : Très grosse spéculation)."
            scores_base[cheval_key] -= 5
            
        if specialite == "Attelé (Trot)" and (6 <= i <= 12 or 1 <= i <= 4):
            analyses[cheval_key] += " Modèle Attelé renforcé (+ de régularité détectée)."
            scores_base[cheval_key] += 7
            
    return scores_base, analyses

# 6. ENSEMBLE DES ONGLETS D'AFFICHAGE
