import streamlit as st
from motore import styles
import motore.ui_components as ui

st.set_page_config(page_title="Ufficio Stampa", layout="wide", page_icon="📰")

if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login nella Dashboard principale.")
    st.stop()

styles.apply_styles()
ui.render_ufficio_stampa()
ui.render_sidebar_footer()