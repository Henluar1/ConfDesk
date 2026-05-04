import streamlit as st
from motore import styles
import motore.ui_components as ui

# --- CONTROLLO ACCESSO ---
if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login nella Dashboard principale.")
    st.stop()

# --- RENDER ---
styles.apply_styles()
ui.render_configurazione()
ui.render_sidebar_footer()
