import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    /* =========================================
       1. OTTIMIZZAZIONE SPAZI (Compattezza)
       ========================================= */
    /* Schiaccia la pagina verso l'alto riducendo il padding di default */
    [data-testid="block-container"] {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }

    /* Compatta i titoli e i sottotitoli */
    h1 {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 2.2rem !important;
        color: #134B8A !important;
        font-weight: 700 !important;
    }
    h2, h3, h4 {
        padding-top: 0rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #134B8A !important;
        font-weight: 700 !important;
    }

    /* Riduci lo spazio dei divider (Le linee orizzontali) */
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }

    /* Compatta gli spazi nei form */
    .stTextInput > div, .stSelectbox > div, .stTextArea > div {
        margin-bottom: 0.2rem !important;
    }
    .stTextInput label, .stSelectbox label {
        padding-bottom: 0.2rem !important;
    }

    /* =========================================
       2. STILI GLOBALI E ISTITUZIONALI
       ========================================= */
    /* Nasconde l'hamburger menu a destra e il footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* FORZA IL COLORE BLU ISTITUZIONALE SOLO SULLA BARRA LATERALE */
    [data-testid="stSidebar"] {
        background-color: #134B8A !important;
    }

    /* Forza il testo del menu laterale a diventare BIANCO */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* MAGIA: Nasconde 'Configurazione' dalla lista in alto, ma lascia il bottone in basso! */
    [data-testid="stSidebarNav"] a[href*="Configurazione"] {
        display: none !important;
    }
    
    /* Assicuriamoci che i campi input siano chiari e leggibili */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 1px solid #CCCCCC !important;
    }

    /* Stile per i Container (Le Card della Home e delle altre pagine) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #FFFFFF !important; 
        border-radius: 12px !important;       
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important; 
        padding: 1.5rem !important;
        border: 1px solid #EAEAEA !important;
        transition: transform 0.2s ease-in-out;
    }

    /* Effetto Hover sulle Card */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08) !important;
    }

    /* Personalizzazione dei bottoni standard */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================================
    # 3. SICUREZZA SIDEBAR
    # =========================================
    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)