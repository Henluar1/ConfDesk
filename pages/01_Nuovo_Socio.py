import streamlit as st
from motore import styles
import motore.ui_components as ui

# 1. SETUP PAGINA (DEVE ESSERE IL PRIMO COMANDO IN ASSOLUTO!)
st.set_page_config(page_title="Nuovo Socio", layout="wide", page_icon="➕")

# 2. CONTROLLO SICUREZZA
if not st.session_state.get("password_correct", False):
    st.warning("Esegui prima il login nella Dashboard principale.")
    st.stop()

# 3. APPLICA GLI STILI (Ora che la pagina è inizializzata, il CSS funzionerà)
styles.apply_styles()

# 4. RENDER DEL FORM
ui.render_form_inserimento()
ui.render_sidebar_footer()