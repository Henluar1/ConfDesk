import streamlit as st

if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login nella Dashboard principale.")
    st.stop()
import streamlit as st
from motore import styles
import motore.ui_components as ui
styles.apply_styles()
# --- SETUP PAGINA ---
st.set_page_config(page_title="Dashboard Analytics", page_icon="📊", layout="wide")
styles.apply_styles()

# --- RENDER ANALYTICS ---
ui.render_analytics()
ui.render_sidebar_footer()