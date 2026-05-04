import streamlit as st

if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login nella Dashboard principale.")
    st.stop()
import streamlit as st
from motore import styles
import motore.ui_components as ui
styles.apply_styles()
st.set_page_config(page_title="Export Documenti", layout="wide", page_icon="📥")
styles.apply_styles()

ui.render_export_documenti()
ui.render_sidebar_footer()