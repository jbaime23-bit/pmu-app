import streamlit as st
import math
import pandas as pd
import altair as alt
import requests
import datetime
import streamlit.components.v1 as components

# --- DÉTECTION ET CHARGEMENT AUTOMATIQUE DE LA COURSE ACTIVE PMU ---
def auto_charger_course_pmu():
    date_jour = datetime.date.today().strftime("%d%m%Y")
    now = datetime.datetime.now()
    heure_actuelle = now.hour * 100 + now.minute
    
    # Étape 1 : Trouver la réunion et la course la plus proche à venir
    url_programme = f"https://pmu.fr{date_jour}"
    reunion_cible, course_cible = "1", "1"
    
    try:
        res_prog = requests.get(url_programme, timeout=4)
        if res_prog.status_code == 200:
            reunions = res_prog.json().get("reunions", [])
            trouve = False
            for r in reunions:
                for c in r.get("courses", []):
                    heure_course = datetime.datetime.fromtimestamp(c.get("heureDepart") / 1000)
                    heure_c_num = heure_course.hour * 100 + heure_course.minute
                    if heure_c_num >= heure_actuelle:
                        reunion_cible = str(r.get("numOfficiel"))
                        course_cible = str(c.get("numOfficiel"))
                        trouve = True
                        break
                if trouve: break
    except Exception:
        pass

    # Étape 2 : Récupérer les partants et les rapports associés
    url_participants = f"https://pmu.fr{date_jour}/R{reunion_cible}/C{course_cible}/participants"
    url_rapports = f"https://pmu.fr{date_jour}/R{reunion_cible}/C{course_cible}/rapports-probables?typePari=SIMPLE_GAGNANT"
    
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
                
                return f"Réunion {reunion_cible} Course {course_cible} (Auto Live PMU)", len(mises_calculees), mises_calculees
    except Exception:
        pass
    
    # Secours Pro stable
    noms_secours = ["Etonnant", "Idao de Tillard", "Hohneck", "Hooker Berry", "Ampia Mede Sm", "Flamme du Goutier", "San Moteur", "Don Fanucci Zet", "Vivid Wise As", "Delia du Pommeux", "Cokstile", "Gu d'Heripre", "Zacon Gio", "Fakir du Lorault", "Chica de Joudes"]
    secours_mises = {f"N°{i+1} - {noms_secours[i]}": float(10000 - (i*600)) for i in range(len(noms_secours))}
    return "R1 Vincennes - Course Principale (Mode Simulation)", 15, secours_mises

# CONFIGURATION PAGE
st.set_page_config(page_title="PMU Pro Ultimate Suite", page_icon="🏇", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

# ACCÈS SÉCURISÉ CLÉ COMPTE UNIQUE ADMIN
MOT_DE_PASSE_ADMIN = "ADMIN7670"

if 'authentifie' not in st.session_state: 
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.title("🔒 Accès Restreint Propriétaire - Plateforme PMU Pro")
    saisie = st.text_input("Entrez votre Clé Administrateur :", type="password")
    if saisie == MOT_DE_PASSE_ADMIN:
        st.session_state.authentifie = True
        st.rerun()
    elif saisie != "":
        st.error("❌ Clé Administrateur incorrecte.")
    st.stop()

# INITIALISATION DES DONNÉES AUTOMATIQUES
if 'nom_course_actuel' not in st.session_state:
    nom_c, nb_p, m_init = auto_charger_course_pmu()
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init

# BARRE LATÉRALE ÉPURÉE
st.sidebar.header("📢 Espace Sponsor Premium")
st.sidebar.markdown('<div style="text-align:center; background-color:#eff6ff; padding:15px; border-radius:8px; border:2px solid #3b82f6;"><b style="color:#1e40af; font-size:12px;">📊 ANNONCE SIDEBAR ACTIVE</b><br><small style="color:#1d4ed8;">Régie Adsterra connectée</small></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Statut Système")
st.sidebar.success("🟢 Mode Automatique Direct")

if st.sidebar.button("🔄 Forcer la mise à jour Live"):
    nom_c, nb_p, m_init = auto_charger_course_pmu()
    st.session_state.nom_course_actuel = nom_c
    st.session_state.mises = m_init
    st.rerun()

type_course = st.sidebar.selectbox("Spécialité :", ["Attelé (Trot)", "Galop", "Haies"])
t_simple = st.sidebar.slider("Taxe Simple (%)", 0, 30, 15) / 100

if st.sidebar.button("🔒 Déconnecter l'interface"):
    st.session_state.authentifie = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("📧 **Contact :** jb.aime23@gmail.com")

# CALCULATEUR MATHÉMATIQUE
def calculer_jeu_simple(mises, taux):
    masse_totale = sum(mises.values())
    if int(masse_totale) == 0: return {k: 99.0 for k in mises.keys()}, 0.0
    masse_net = float(masse_totale) * (1.0 - float(taux))
    return {cheval: max(math.floor((masse_net / float(mise)) * 100) / 100, 1.10) if mise > 0 else 99.0 for cheval, mise in mises.items()}, masse_totale

cotes_s, m_totale = calculer_jeu_simple(st.session_state.mises, t_simple)

# AUTO-SÉLECTION DE VOS 9 MEILLEURS CHIFFRES SELON VOS RÈGLES D'EXPERT
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

# INTERFACE INTERACTIVE
st.title(" 🏇 PMU Pro Suite Ultimate Hub v9.0")

# --- SCRIPT ADSTERRA BANNIÈRE DU HAUT ---
code_adsterra_banner = '<div style="text-align:center; margin-bottom:15px;"><script type="text/javascript">atOptions = {"key" : "b9b40b1c4e412de03b6465589ab82662","format" : "iframe","height" : 90,"width" : 728,"params" : {}};</script><script type="text/javascript" src="https://highrevenueformat.com"></script></div>'
components.html(code_adsterra_banner, height=105)

# --- BOUTON UNIVERSEL REGARDER LE LIVE ---
st.markdown("""
<div style="background-color:#ffffff; padding:15px; border-radius:10px; border:1px solid #e2e8f0; text-align:center; margin-bottom:20px;">
    <a href="https://lescourseshippiques.fr" target="_blank" style="text-decoration:none;">
        <button style="background-color:#ef4444; color:white; border:none; padding:12px 25px; font-size:15px; font-weight:bold; border-radius:6px; cursor:pointer; width:100%; max-width:350px;">
            ▶️ LNCER LE STREAMING EN DIRECT EQUIDIA
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
    
    # --- SCRIPT ADSTERRA 2 ---
  
