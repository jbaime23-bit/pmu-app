import streamlit as st
import streamlit.components.v1 as components

# --- CONFIGURATION PREMIUM DE LA PAGE ---
st.set_page_config(page_title="PMU Pro Ultimate Hub", page_icon="🏇", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .stApp {background-color: #0f172a;}
    .main-title {text-align: center; color: #f8fafc; font-size: 24px; font-weight: bold; margin-bottom: 30px;}
    .ad-title {color: #3b82f6; font-size: 14px; text-align: center; font-weight: bold; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏇 ZONE DE TEST PUBLICITAIRE (v17.0)</div>', unsafe_allow_html=True)

# ==========================================
# 📺 ESPACE 1 : BANNIÈRE DU HAUT (728x90)
# ==========================================
st.markdown('<div class="ad-title">📺 BANNIÈRE HAUTE (728x90) :</div>', unsafe_allow_html=True)

code_adsterra_banner_haut = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; min-height: 90px; overflow-x: auto;">
  <div style="width: 728px; height: 90px; flex-shrink: 0;">
    <script type="text/javascript">
      atOptions = {'key' : 'b9b40b1c4e412de03b6465589ab82662', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {}};
    </script>
    <script type="text/javascript" src="https://highrevenueformat.com"></script>
  </div>
</div>
"""
components.html(code_adsterra_banner_haut, height=110, scrolling=True)


# ==========================================
# 📺 ESPACE 2 : POPUNDER INTERSTITIEL VIDÉO
# ==========================================
st.markdown('<div class="ad-title">📺 SCRIPT POPUNDER / INTERSTITIEL :</div>', unsafe_allow_html=True)

code_popunder_video = """
<div style="text-align: center; padding: 10px; background-color: #1e293b; border-radius: 8px; color: #94a3b8; font-size: 12px; max-width: 400px; margin: 0 auto;">
  Le script invisible ci-dessous se déclenche automatiquement en arrière-plan.
</div>
<script async="async" data-cfasync="false" src="https://profitableratecpmnetwork.com"></script>
<div id="container-548477c48bb33989924ab69d7a4e0cc1"></div>
"""
components.html(code_popunder_video, height=60, scrolling=False)


# ==========================================
# 📺 ESPACE 3 : BANNIÈRE DU BAS (728x90)
# ==========================================
st.markdown('<div class="ad-title">📺 BANNIÈRE BASSE (728x90) :</div>', unsafe_allow_html=True)

code_adsterra_banner_bas = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; min-height: 90px; overflow-x: auto;">
  <div style="width: 728px; height: 90px; flex-shrink: 0;">
    <script type="text/javascript">
      atOptions = {'key' : 'b9b40b1c4e412de03b6465589ab82662', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {}};
    </script>
    <script type="text/javascript" src="https://highrevenueformat.com"></script>
  </div>
</div>
"""
components.html(code_adsterra_banner_bas, height=115, scrolling=True)
