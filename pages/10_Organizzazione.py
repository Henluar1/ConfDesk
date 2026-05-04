import streamlit as st
from motore import styles
import motore.ui_components as ui

# 1. SETUP PAGINA
st.set_page_config(page_title="Organizzazione", layout="wide", page_icon="👔")

# 2. CONTROLLO SICUREZZA
if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login nella Dashboard principale.")
    st.stop()

# 3. APPLICA STILI
styles.apply_styles()

# 4. RENDER
ui.render_organizzazione()
ui.render_sidebar_footer()