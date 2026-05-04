import streamlit as st
import os

# 1. SETUP PAGINA (Deve essere il primo comando assoluto)
st.set_page_config(page_title="MemberFlow - Assafrica", layout="wide", page_icon="🏛️")
st.logo("media/logo_confdesk.png")

# ==========================================
# 🚀 ROUTING PUBBLICO (NO PASSWORD)
# ==========================================
page = st.query_params.get("page")
evento_id = st.query_params.get("evento")

if page == "registrazione":
    from motore import styles, ui_components as ui
    from motore.database_manager import inizializza_db
    styles.apply_styles(); inizializza_db()
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;} [data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    ui.render_modulo_pubblico()
    st.stop() 

elif evento_id:
    from motore import styles, ui_components as ui
    from motore.database_manager import inizializza_db
    styles.apply_styles(); inizializza_db()
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;} [data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    ui.render_modulo_evento(evento_id)
    st.stop()

# 2. Modulo Iscrizione Evento (?evento=123)
evento_id = st.query_params.get("evento")
if evento_id:
    from motore import styles
    import motore.ui_components as ui
    from motore.database_manager import inizializza_db
    styles.apply_styles()
    inizializza_db()
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;} [data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    ui.render_modulo_evento(evento_id)
    st.stop()


# ==========================================
# 🔐 AREA RISERVATA (CON PASSWORD)
# ==========================================

# 2. FUNZIONE CONTROLLO PASSWORD
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <h1>🔐 Accesso Riservato</h1>
            <p>Inserisci la password per accedere al database Confindustria Assafrica & Mediterraneo</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        password_input = st.text_input("Password", type="password", placeholder="Scrivi qui...")
        if st.button("Entra nel Sistema", use_container_width=True, type="primary"):
            if password_input == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Password errata. Riprova.")
    
    st.navigation([st.Page(lambda: None, title="Login richiesto", icon="🔒")]).run()
    st.stop()

# 3. ESECUZIONE CONTROLLO SICUREZZA
check_password()

# --- DA QUI IN POI L'UTENTE È LOGGATO ---
from motore import styles
from motore.database_manager import inizializza_db, leggi_config
import motore.ui_components as ui

styles.apply_styles()
inizializza_db()

for folder in ["media/loghi_soci", "exports", "risorse"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

conf = leggi_config()
nome_ass = conf.get('nome_associazione', 'Assafrica')

def render_home():
    if 'welcome' not in st.session_state:
        st.toast(f"Connessione stabilita con il database {nome_ass}", icon="🛰️")
        st.session_state['welcome'] = True

    col_img, col_testo = st.columns([1, 5])
    with col_img:
        # Mostra il logo in grande sulla home
        if os.path.exists("media/logo_confdesk.png"):
            st.image("media/logo_confdesk.png", use_container_width=True)
    with col_testo:
        st.title(f"🏛️ {nome_ass}")
        st.subheader("Powered by ConfDesk™ - Digital Association Management")
    
    # Info per l'Admin sul link pubblico
    st.info(f"🌐 **Link Modulo Adesione Pubblico:** I nuovi soci possono iscriversi autonomamente a questo link: `http://localhost:8501/?page=registrazione` *(Copia e invia via email)*")
    st.divider()

    st.markdown("#### 📌 Navigazione Rapida")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown("### 👥 Gestione")
            st.write("Anagrafica, nuovi soci e membri del team.")
            st.page_link("pages/02_Gestione_Anagrafiche.py", label="Apri Anagrafiche", icon="📋")
            st.page_link("pages/01_Nuovo_Socio.py", label="Aggiungi Socio", icon="➕")
            st.page_link("pages/10_Organizzazione.py", label="Gestione Team", icon="👔")

    with col2:
        with st.container(border=True):
            st.markdown("### 📈 Intelligence")
            st.write("Analisi geografica e BI del network.")
            st.page_link("pages/04_Dashboard_Analytics.py", label="Vedi Analytics", icon="📊")
            st.page_link("pages/06_Mappa_Network.py", label="Apri Mappa", icon="🌍")

    with col3:
        with st.container(border=True):
            st.markdown("### 🎨 Marketing")
            st.write("Generazione cataloghi e grafiche social.")
            st.page_link("pages/05_Export_Documenti.py", label="Genera Cataloghi", icon="📄")
            st.page_link("pages/07_Marketing.py", label="Marketing Studio", icon="🎨")

    with col4:
        with st.container(border=True):
            st.markdown("### 📚 Risorse")
            st.write("Kit primo contatto e modulistica.")
            st.page_link("pages/08_Risorse.py", label="Apri Libreria", icon="📂")

    st.divider()
    st.markdown("#### ⚙️ Stato del Sistema")
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Stato Database", value="Online 🟢", delta="Sincronizzato")
    m2.metric(label="Versione Software", value="v3.2", delta="Public Forms Enabled", delta_color="off")
    m3.metric(label="Log Attività", value="Nessun Errore", delta="Check in tempo reale")
    
    ui.render_sidebar_footer()

pg = st.navigation({
    "Main": [st.Page(render_home, title="Dashboard", icon="🏠")],
    "Anagrafica & Eventi": [
        st.Page("pages/01_Nuovo_Socio.py", title="Nuovo Socio", icon="➕"),
        st.Page("pages/02_Gestione_Anagrafiche.py", title="Gestione Soci", icon="📋"),
        st.Page("pages/11_Eventi.py", title="Eventi e Registrazioni", icon="📅"),
        st.Page("pages/10_Organizzazione.py", title="Team & Organizzazione", icon="👔"),
        st.Page("pages/03_Amministrazione.py", title="Amministrazione", icon="💸"),
    ],
    "Analisi & BI": [
        st.Page("pages/04_Dashboard_Analytics.py", title="Analytics", icon="📊"),
        st.Page("pages/06_Mappa_Network.py", title="Mappa Network", icon="🌍"),
    ],
    "Marketing & Documenti": [
        st.Page("pages/05_Export_Documenti.py", title="Export Documenti", icon="📄"),
        st.Page("pages/12_Ufficio_Stampa.py", title="Ufficio Stampa", icon="📰"), # <-- Aggiunta!
        st.Page("pages/07_Marketing.py", title="Marketing Studio", icon="🎨"),
    ],
    "Archivio": [
        st.Page("pages/08_Risorse.py", title="Risorse & Kit", icon="📂"),
    ],
    "Impostazioni": [
    st.Page("pages/09_Impostazioni.py", title="Configurazione", icon="⚙️"),
    st.Page("pages/13_Supporto_IT.py", title="Supporto Tecnico", icon="🛠️"),
]
})
pg.run()
