import streamlit as st
from motore import styles
import motore.ui_components as ui

st.set_page_config(page_title="Supporto IT", layout="wide", page_icon="🛠️")

if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login.")
    st.stop()

styles.apply_styles()
# Chiamiamo la nuova funzione interna!
ui.render_supporto_tecnico()
ui.render_sidebar_footer()