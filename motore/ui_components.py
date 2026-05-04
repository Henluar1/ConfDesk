import streamlit as st
import pandas as pd
import plotly.express as px
import os
import urllib.parse
import base64
import json
from PIL import Image
from io import BytesIO

# ⚠️ ATTENZIONE: Importiamo anche le nuove funzioni del Team!

from motore.database_manager import (
    leggi_soci, aggiorna_socio, elimina_socio, aggiungi_socio, 
    leggi_config, salva_config, 
    leggi_team, aggiungi_membro_team, elimina_membro_team, aggiorna_membro_team,
    leggi_eventi, aggiungi_evento, elimina_evento, leggi_partecipanti, aggiungi_partecipante,
    leggi_giornalisti, aggiungi_giornalista, aggiorna_giornalista, elimina_giornalista,
    leggi_ticket, aggiungi_ticket, chiudi_ticket, elimina_ticket
)
# --- COSTANTI GLOBALI ---
PAESI_AFRICA = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Camerun", "Capo Verde", 
    "Ciad", "Comore", "Costa d'Avorio", "Egitto", "Eritrea", "Eswatini", "Etiopia", "Gabon", 
    "Gambia", "Ghana", "Gibuti", "Guinea", "Guinea Equatoriale", "Guinea-Bissau", "Kenya", 
    "Lesotho", "Liberia", "Libia", "Madagascar", "Malawi", "Mali", "Marocco", "Mauritania", 
    "Mauritius", "Mozambico", "Namibia", "Niger", "Nigeria", "Repubblica Centrafricana", 
    "Repubblica del Congo", "Repubblica Democratica del Congo", "Ruanda", "Sahara Occidentale", 
    "Sant'Elena", "São Tomé e Príncipe", "Senegal", "Seychelles", "Sierra Leone", "Somalia", 
    "Sudafrica", "Sudan", "Sudan del Sud", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
]

OPZIONI_FATTURATO = [
    "Non specificato",
    "startup",
    "fino a 2 milioni di euro",
    "tra 2 e 10 milioni di euro",
    "tra 10 e 50 milioni di euro",
    "oltre 50 milioni di euro"
]

# --- GESTIONE DINAMICA SETTORI ---
FILE_SETTORI = "config_settori.json"
SETTORI_BASE = [
    "ENERGIA & AMBIENTE", "MACCHINARI & IMPIANTI", "ICT & DIGITALE", 
    "EDILIZIA & INFRASTRUTTURE", "AGROALIMENTARE", "LOGISTICA & TRASPORTI", 
    "CHIMICA & GOMMA", "SERVIZI ALLE IMPRESE", "BANCHE", "ALTRO"
]

def ottieni_categorie():
    if not os.path.exists(FILE_SETTORI):
        with open(FILE_SETTORI, "w") as f:
            json.dump(SETTORI_BASE, f)
        return SETTORI_BASE
    with open(FILE_SETTORI, "r") as f:
        return json.load(f)

def salva_categorie(nuove_categorie):
    with open(FILE_SETTORI, "w") as f:
        json.dump(nuove_categorie, f)

# ==========================================
# 01. COMPONENTE: NUOVO SOCIO
# ==========================================
def render_form_inserimento():
    st.markdown("<h2 style='color: #0033A0;'>➕ Registra Nuova Azienda</h2>", unsafe_allow_html=True)
    
    # BOX CON IL LINK PUBBLICO
    st.info("🌐 **Link Modulo Adesione Pubblico:** Copia e invia questo link alle aziende esterne per farle registrare in autonomia (finiranno nello stato 'In attesa'):\n\n👉 **`http://localhost:8501/?page=registrazione`**")
    
    st.markdown("Oppure aggiungi un'azienda al Catalogo tramite inserimento manuale o importazione massiva da Excel.")
    st.divider()
    
    tab1, tab2 = st.tabs(["✍️ Inserimento Singolo", "📁 Importazione Massiva (Excel)"])
    
    with tab1:
        with st.form("form_nuovo", clear_on_submit=True):
            st.markdown("#### 🏢 Dati Generali")
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Ragione Sociale *")
                cat = st.selectbox("Settore Merceologico", ottieni_categorie())
                ref = st.text_input("Referente A&M")
                pagato = st.selectbox("Stato Socio", ["Pagato", "In attesa"])
            with c2:
                mail = st.text_input("Email")
                web = st.text_input("Sito Web")
                vol_affari = st.selectbox("Volume d'affari", OPZIONI_FATTURATO)
            
            st.divider()
            
            st.markdown("#### 🌍 Dettagli Operativi e Immagini")
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("**Operatività in Africa**")
                tutto_continente = st.toggle("Opera in tutto il continente (Pan-Africana)")
                paesi_selezionati = ["Tutta l'Africa"] if tutto_continente else st.multiselect(
                    "Seleziona Paesi", PAESI_AFRICA, label_visibility="collapsed"
                )
            with c4:
                c_logo, c_cover = st.columns(2)
                logo_file = c_logo.file_uploader("🖼️ Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
                cover_file = c_cover.file_uploader("📸 Foto Presentazione", type=["png", "jpg", "jpeg"])
                st.caption("Tip: La foto sarà lo sfondo della locandina.")
            
            st.divider()
            
            st.markdown("#### 📝 Testi Descrittivi")
            c_desc1, c_desc2 = st.columns(2)
            with c_desc1:
                desc = st.text_area("Descrizione Breve (Per il catalogo globale)", height=150)
            with c_desc2:
                desc_lunga = st.text_area("Descrizione Estesa (Per Locandina One-Pager)", height=150)
            
            if st.form_submit_button("💾 SALVA NEL DATABASE", type="primary", use_container_width=True):
                if nome and paesi_selezionati:
                    path_logo_finale = ""
                    path_cover_finale = ""
                    
                    if not os.path.exists("media/loghi_soci"): os.makedirs("media/loghi_soci")
                    if not os.path.exists("media/foto_presentazione"): os.makedirs("media/foto_presentazione")
                    
                    nome_sicuro = "".join(x for x in nome if x.isalnum() or x in " ").replace(' ', '_').upper()

                    if logo_file:
                        est = logo_file.name.split('.')[-1].lower()
                        path_logo_finale = f"media/loghi_soci/{nome_sicuro}_LOGO.{est}"
                        with open(path_logo_finale, "wb") as f:
                            f.write(logo_file.getbuffer())
                    
                    if cover_file:
                        est = cover_file.name.split('.')[-1].lower()
                        path_cover_finale = f"media/foto_presentazione/{nome_sicuro}_COVER.{est}"
                        with open(path_cover_finale, "wb") as f:
                            f.write(cover_file.getbuffer())
                    
                    stringa_paesi = ",".join(paesi_selezionati)
                    aggiungi_socio(nome, cat, ref, mail, web, desc, desc_lunga, path_logo_finale, path_cover_finale, pagato, stringa_paesi, vol_affari)
                    st.toast(f"Azienda {nome} aggiunta con successo!", icon="✅")
                else:
                    st.error("⚠️ La Ragione Sociale e almeno un Paese sono obbligatori.")

    with tab2:
        st.info("💡 **Tip:** Carica un file Excel. L'intelligenza del sistema mapperà automaticamente le colonne. I loghi andranno aggiunti dal pannello Gestione.")
        file_excel = st.file_uploader("Carica file Excel (.xlsx)", type=["xlsx"])
        
        if file_excel:
            df_raw = pd.read_excel(file_excel, header=None)
            header_row_index = None
            for i, row in df_raw.iterrows():
                vals = [str(v).lower().strip() for v in row.values]
                if 'nome' in vals or 'ragione sociale' in vals:
                    header_row_index = i
                    break
            
            if header_row_index is not None:
                df_import = pd.read_excel(file_excel, skiprows=header_row_index)
                col_map = {str(c).lower().strip(): c for c in df_import.columns}
                
                def get_smart_val(row_data, alias_list, default=""):
                    for alias in alias_list:
                        if alias in col_map:
                            val = row_data[col_map[alias]]
                            return str(val).strip() if pd.notnull(val) else default
                    return default

                if st.button("🚀 AVVIA IMPORTAZIONE MASSIVA", type="primary"):
                    progress_bar = st.progress(0)
                    for i, index in enumerate(df_import.index):
                        row = df_import.loc[index]
                        nome_val = get_smart_val(row, ['nome', 'ragione sociale', 'azienda'], "Socio Anonimo")
                        if nome_val == "Socio Anonimo" or str(nome_val) == "nan": continue
                        
                        aggiungi_socio(
                            nome_val, 
                            get_smart_val(row, ['categoria', 'settore', 'area'], "ALTRO"), 
                            get_smart_val(row, ['referente', 'contatto'], ""), 
                            get_smart_val(row, ['email', 'mail'], ""), 
                            get_smart_val(row, ['sito', 'web', 'url'], ""), 
                            get_smart_val(row, ['descrizione', 'attività'], ""), 
                            "", "", "", "Pagato", 
                            get_smart_val(row, ['sede', 'paesi', 'operatività'], "Tutta l'Africa"),
                            "Non specificato"
                        )
                        progress_bar.progress((i + 1) / len(df_import))
                    st.toast("Importazione anagrafiche completata!", icon="🎉")

# ==========================================
# 02. COMPONENTE: GESTIONE ANAGRAFICHE
# ==========================================
def render_gestione():
    st.markdown("<h2 style='color: #0033A0;'>📋 Gestione Anagrafiche</h2>", unsafe_allow_html=True)
    df = leggi_soci()
    
    if not df.empty:
        st.info("💡 **Modifica Rapida:** Clicca sulle celle della tabella per modificare i testi base. L'editor avanzato in basso permette di gestire i testi lunghi, i loghi e i paesi.")
        
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "logo_path": None,
                "immagine_copertina_path": None,
                "descrizione_lunga": None,
                "nome": st.column_config.TextColumn("Ragione Sociale", width="medium"),
                "categoria": st.column_config.SelectboxColumn("Settore", options=ottieni_categorie()),
                "volume_affari": st.column_config.SelectboxColumn("Fatturato", options=OPZIONI_FATTURATO),
                "pagato": st.column_config.SelectboxColumn("Stato", options=["Pagato", "In attesa"]),
                "sito": st.column_config.LinkColumn("Sito Web"),
                "sede": st.column_config.TextColumn("Operatività (Vedi Editor)", disabled=True)
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            height=400
        )

        if st.button("💾 SALVA MODIFICHE TABELLA", type="primary"):
            for _, row in edited_df.iterrows():
                if pd.notna(row.get('id')):
                    dl = str(row['descrizione_lunga']) if 'descrizione_lunga' in row else ''
                    lp = str(row['logo_path']) if 'logo_path' in row else ''
                    ic = str(row['immagine_copertina_path']) if 'immagine_copertina_path' in row else ''
                    va = str(row['volume_affari']) if 'volume_affari' in row else 'Non specificato'
                    
                    aggiorna_socio(
                        row['id'], row['nome'], row['categoria'], row['referente'], 
                        row['email'], row['sito'], row['descrizione'], dl,
                        lp, ic, row['pagato'], row['sede'], va
                    )
            st.toast("Dati testuali sincronizzati con il database!", icon="🔄")

        st.divider()

        st.markdown("#### ⚙️ Editor Avanzato: Testi, Media e Paesi Operativi")
        with st.expander("Apri per modificare la descrizione lunga, le immagini o la copertura geografica"):
            nomi_soci = sorted(df['nome'].tolist())
            azienda_scelta = st.selectbox("Seleziona Azienda da modificare:", nomi_soci)
            socio_target = df[df['nome'] == azienda_scelta].iloc[0]
            
            st.divider()
            
            # --- ZONA MEDIA ---
            st.markdown("**🖼️ Gestione Media**")
            c_logo, c_cover = st.columns(2)
            
            with c_logo:
                st.markdown("**Logo Aziendale**")
                logo_attuale = socio_target.get('logo_path', '')
                if pd.notna(logo_attuale) and str(logo_attuale).strip() != "" and os.path.exists(str(logo_attuale)):
                    st.image(str(logo_attuale), caption="Logo attuale", width=150)
                else:
                    st.warning("Nessun logo presente.")
                nuovo_logo = st.file_uploader(f"Sostituisci logo", type=["png", "jpg", "jpeg"], key="up_logo")
            
            with c_cover:
                st.markdown("**Foto di Presentazione (Sfondo Locandina)**")
                cover_attuale = socio_target.get('immagine_copertina_path', '') if 'immagine_copertina_path' in socio_target else ''
                if pd.notna(cover_attuale) and str(cover_attuale).strip() != "" and os.path.exists(str(cover_attuale)):
                    st.image(str(cover_attuale), caption="Foto presentazione attuale", width=250)
                else:
                    st.warning("Nessuna foto di presentazione presente.")
                nuovo_cover = st.file_uploader(f"Sostituisci foto presentazione", type=["png", "jpg", "jpeg"], key="up_cover")
            
            st.divider()

            # --- Altri Dati ---
            st.markdown("**🌍 Copertura Geografica e Dimensioni**")
            c_geo, c_fatt = st.columns(2)
            with c_geo:
                sede_attuale = str(socio_target.get('sede', ''))
                is_pan_africana = (sede_attuale == "Tutta l'Africa")
                tutto_continente_edit = st.toggle("Opera in tutto il continente (Pan-Africana)", value=is_pan_africana, key="tgl_edit")
                
                if tutto_continente_edit:
                    nuovi_paesi = ["Tutta l'Africa"]
                else:
                    paesi_preesistenti = [p.strip() for p in sede_attuale.split(',') if p.strip() in PAESI_AFRICA] if (sede_attuale and not is_pan_africana) else []
                    nuovi_paesi = st.multiselect("Modifica Paesi:", options=PAESI_AFRICA, default=paesi_preesistenti, key="ms_edit")
            
            with c_fatt:
                va_attuale = str(socio_target.get('volume_affari', 'Non specificato'))
                nuovo_vol_affari = st.selectbox("Modifica Volume d'affari", OPZIONI_FATTURATO, index=OPZIONI_FATTURATO.index(va_attuale) if va_attuale in OPZIONI_FATTURATO else 0)

            st.markdown("<br>**📝 Testi Aziendali**", unsafe_allow_html=True)
            c_testo1, c_testo2 = st.columns(2)
            
            desc_breve_attuale = str(socio_target.get('descrizione', ''))
            desc_lunga_attuale = str(socio_target.get('descrizione_lunga', '')) if 'descrizione_lunga' in socio_target else ''
            
            nuova_desc_breve = c_testo1.text_area("Descrizione Breve", value=desc_breve_attuale, height=130)
            nuova_desc_lunga = c_testo2.text_area("Descrizione Estesa", value=desc_lunga_attuale, height=130)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 CONFERMA MODIFICHE AVANZATE", type="primary", use_container_width=True):
                if not os.path.exists("media/loghi_soci"): os.makedirs("media/loghi_soci")
                if not os.path.exists("media/foto_presentazione"): os.makedirs("media/foto_presentazione")
                nome_sicuro = "".join(x for x in azienda_scelta if x.isalnum() or x in " ").replace(' ', '_').upper()

                path_logo_finale = logo_attuale
                if nuovo_logo is not None:
                    est = nuovo_logo.name.split('.')[-1].lower()
                    path_logo_finale = f"media/loghi_soci/{nome_sicuro}_LOGO.{est}"
                    with open(path_logo_finale, "wb") as f:
                        f.write(nuovo_logo.getbuffer())
                        
                path_cover_finale = cover_attuale
                if nuovo_cover is not None:
                    est = nuovo_cover.name.split('.')[-1].lower()
                    path_cover_finale = f"media/foto_presentazione/{nome_sicuro}_COVER.{est}"
                    with open(path_cover_finale, "wb") as f:
                        f.write(nuovo_cover.getbuffer())
                
                stringa_paesi_aggiornata = ",".join(nuovi_paesi)
                try:
                    aggiorna_socio(
                        int(socio_target['id']), str(socio_target['nome']), str(socio_target['categoria']), 
                        str(socio_target['referente']), str(socio_target['email']), str(socio_target['sito']), 
                        nuova_desc_breve, nuova_desc_lunga, path_logo_finale, path_cover_finale, str(socio_target['pagato']), stringa_paesi_aggiornata, nuovo_vol_affari
                    )
                    st.toast(f"Dati di {azienda_scelta} aggiornati!", icon="✅")
                    st.rerun() 
                except Exception as e:
                    st.error(f"Errore durante l'aggiornamento: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Zona Pericolo (Eliminazione Definitiva)"):
            st.warning("Attenzione: l'eliminazione è irreversibile.")
            id_del = st.number_input("ID Socio da rimuovere", step=1, value=0)
            if st.button("ELIMINA SOCIO"):
                elimina_socio(id_del)
                st.toast(f"Socio {id_del} eliminato.", icon="🗑️")
    else:
        st.info("Il database è attualmente vuoto.")

# ==========================================
# 03. COMPONENTE: ANALYTICS
# ==========================================
def render_analytics():
    st.markdown("<h2 style='color: #0033A0;'>📊 Business Intelligence</h2>", unsafe_allow_html=True)
    df = leggi_soci()
    
    if not df.empty:
        lista_paesi_flat = []
        heatmap_data = []
        for _, row in df.iterrows():
            p_str = str(row.get('sede', ''))
            paesi = PAESI_AFRICA if p_str == "Tutta l'Africa" else [p.strip() for p in p_str.split(",") if p.strip()]
            for p in paesi:
                if p in PAESI_AFRICA:
                    lista_paesi_flat.append(p)
                    heatmap_data.append({'Settore': row['categoria'], 'Paese': p})
            if p_str == "Tutta l'Africa":
                lista_paesi_flat.append("Pan-Africana")

        df_geo_counts = pd.Series(lista_paesi_flat).value_counts().reset_index()
        df_geo_counts.columns = ['Paese', 'Numero Aziende']

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Totale Soci", len(df))
        m2.metric("Mercati Presidiati", len(df_geo_counts[df_geo_counts['Paese'] != "Pan-Africana"]))
        m3.metric("Aziende Pan-Africane", len(df[df['sede'] == "Tutta l'Africa"]))
        reg = (len(df[df['pagato'] == 'Pagato'])/len(df)*100) if len(df) > 0 else 0
        m4.metric("Regolarità Quote", f"{reg:.1f}%")

        st.divider()

        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown("#### 🏆 Top 15 Mercati Strategici")
            top_15 = df_geo_counts[df_geo_counts['Paese'] != "Pan-Africana"].head(15)
            fig_bar = px.bar(top_15, x='Numero Aziende', y='Paese', orientation='h',
                             color='Numero Aziende', color_continuous_scale='Blues', text_auto=True)
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, showlegend=False, template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("#### 🏗️ Treemap dei Settori")
            fig_tree = px.treemap(df, path=['categoria', 'nome'], color='categoria', template="plotly_white")
            fig_tree.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig_tree, use_container_width=True)

        st.divider()

        c3, c4 = st.columns([0.5, 0.5])
        
        with c3:
            st.markdown("#### 🛰️ Radar di Penetrazione: Settore vs Paesi")
            if heatmap_data:
                df_heat = pd.DataFrame(heatmap_data)
                df_h_counts = df_heat.groupby(['Settore', 'Paese']).size().reset_index(name='Presenze')
                fig_heat = px.density_heatmap(df_h_counts, x="Paese", y="Settore", z="Presenze",
                                              color_continuous_scale="GnBu", text_auto=True)
                fig_heat.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig_heat, use_container_width=True)
        
        with c4:
            st.markdown("#### 💰 Distribuzione Dimensionale (Fatturato)")
            if 'volume_affari' in df.columns:
                df_fatturato = df[df['volume_affari'] != 'Non specificato']['volume_affari'].value_counts().reset_index()
                df_fatturato.columns = ['Fascia', 'Numero Aziende']
                
                if not df_fatturato.empty:
                    fig_pie = px.pie(df_fatturato, values='Numero Aziende', names='Fascia', hole=0.4, 
                                     color_discrete_sequence=px.colors.sequential.Blues_r)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(template="plotly_white", height=400, showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Nessun dato sul fatturato disponibile per generare il grafico.")
            else:
                 st.info("Colonna volume_affari non trovata nel database.")
                 
# ==========================================
# 04. COMPONENTE: AMMINISTRAZIONE
# ==========================================
def render_amministrazione():
    st.markdown("<h2 style='color: #0033A0;'>💸 Amministrazione e Solleciti</h2>", unsafe_allow_html=True)
    df = leggi_soci()
    
    if not df.empty:
        df_attesa = df[df['pagato'] == 'In attesa']
        
        c1, c2 = st.columns([1, 3])
        c1.metric("Quote da sollecitare", len(df_attesa))
        
        st.divider()
        
        if not df_attesa.empty:
            st.info("💡 Clicca su 'Invia Sollecito' per aprire il tuo programma di posta con un'email precompilata.")
            
            col1, col2, col3, col4 = st.columns([3, 2, 2.5, 2])
            col1.caption("AZIENDA")
            col2.caption("REFERENTE")
            col3.caption("EMAIL")
            col4.caption("AZIONE")
            
            for _, row in df_attesa.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2.5, 2])
                
                col1.write(f"**{row['nome']}**")
                col2.write(row['referente'] if pd.notna(row['referente']) else "Non specificato")
                col3.write(row['email'] if pd.notna(row['email']) else "N/A")
                
                with col4:
                    if pd.notna(row['email']) and str(row['email']).strip() != "":
                        oggetto = urllib.parse.quote("Confindustria Assafrica & Mediterraneo - Sollecito Quota Associativa 2026")
                        nome_ref = str(row['referente']) if pd.notna(row['referente']) else "Responsabile"
                        
                        corpo = urllib.parse.quote(
                            f"Gentile {nome_ref},\n\n"
                            f"Con la presente le ricordiamo che la quota associativa per l'azienda {row['nome']} "
                            f"risulta attualmente 'In attesa' di saldo.\n\n"
                            f"La preghiamo di provvedere al più presto per garantire la continuità dei servizi.\n\n"
                            f"Restiamo a disposizione per qualsiasi chiarimento.\n\n"
                            f"Cordiali saluti,\n"
                            f"Segreteria Assafrica"
                        )
                        
                        mailto_link = f"mailto:{row['email']}?subject={oggetto}&body={corpo}"
                        st.link_button("✉️ INVIA SOLLECITO", mailto_link, use_container_width=True)
                    else:
                        st.button("Manca Email", disabled=True, key=f"dis_{row['id']}", use_container_width=True)
                
                st.markdown("<hr style='margin: 10px 0px; opacity: 0.1;'>", unsafe_allow_html=True)
                
        else:
            st.success("🎉 Grandioso! Tutte le aziende risultano in regola con i pagamenti.")
    else:
        st.info("Il database è attualmente vuoto.")

# ==========================================
# 05. COMPONENTE: EXPORT DOCUMENTI & DATI
# ==========================================

def genera_excel_avanzato(df):
    output = BytesIO()
    
    colonne_export = [
        'nome', 'categoria', 'referente', 'email', 'sito',
        'sede', 'volume_affari', 'pagato'
    ]
    
    for col in colonne_export:
        if col not in df.columns:
            df[col] = "Non specificato"
            
    df['presenza_geografica'] = df['sede']
            
    df_export = df[['nome', 'categoria', 'referente', 'email', 'sito', 'presenza_geografica', 'volume_affari', 'pagato']]
    
    df_export = df_export.rename(columns={
        'nome': 'Ragione Sociale',
        'categoria': 'Settore Merceologico',
        'referente': 'Referente',
        'email': 'Email Contatto',
        'sito': 'Sito Web',
        'presenza_geografica': 'Mercati di Interesse / Presidiati',
        'volume_affari': 'Dimensione Aziendale (Fatturato)',
        'pagato': 'Stato Quota'
    })

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Anagrafica Soci')
        
    return output.getvalue()


def render_export_documenti():
    st.markdown("<h2 style='color: #0033A0;'>📥 Centro Esportazione Documenti</h2>", unsafe_allow_html=True)
    st.markdown("Genera documenti impaginati globali o schede individuali basate sui dati attuali del network.")
    st.divider()

    df_attuali = leggi_soci()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📚 **Catalogo Ufficiale**\n\nGenera l'impaginato completo.")
        if st.button("🚀 GENERA CATALOGO PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Generazione impaginato in corso..."):
                    from motore.pdf_engine import genera_catalogo
                    file_path = genera_catalogo(df_attuali) 
                    with open(file_path, "rb") as f:
                        st.download_button("⬇️ SCARICA CATALOGO", f, "Catalogo_Assafrica_2026.pdf", "application/pdf", use_container_width=True, type="primary")
            else: 
                st.warning("Database vuoto.")
                
    with c2:
        st.warning("📈 **Report Analitico**\n\nStatistiche e copertura geografica.")
        if st.button("📑 GENERA REPORT PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Analisi dati e generazione grafici..."):
                    from motore.report_generator import genera_report_dati
                    path_rep = genera_report_dati(df_attuali)
                    with open(path_rep, "rb") as f:
                        st.download_button("⬇️ SCARICA REPORT", f, "Report_Analisi_2026.pdf", "application/pdf", use_container_width=True, type="primary")
            else: 
                st.warning("Database vuoto.")
                
    with c3:
        st.success("📊 **Database Aziendale (Excel)**\n\nExport con dimensioni e mercati.")
        if st.button("💾 GENERA EXCEL AVANZATO", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Preparazione file Excel..."):
                    excel_data = genera_excel_avanzato(df_attuali)
                    st.download_button(
                        label="⬇️ SCARICA EXCEL",
                        data=excel_data,
                        file_name="Anagrafica_Soci_Avanzata.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
            else: 
                st.warning("Database vuoto.")

    st.divider()
    st.markdown("#### 📄 Esporta Scheda Singola Socio (One-Pager)")
    st.caption("Genera un documento di presentazione istituzionale in A4 per un singolo associato.")

    if not df_attuali.empty:
        nomi_soci = sorted(df_attuali['nome'].tolist())
        col_sel, col_btn = st.columns([3, 1])
        socio_nome = col_sel.selectbox("Seleziona l'Associato", nomi_soci, label_visibility="collapsed")
        
        if col_btn.button("✨ COMPILA ONE-PAGER", use_container_width=True):
            socio_data = df_attuali[df_attuali['nome'] == socio_nome].iloc[0]
            with st.spinner(f"Creazione scheda istituzionale per {socio_nome}..."):
                from motore.pdf_engine import genera_scheda_socio
                path_scheda = genera_scheda_socio(socio_data)
                if os.path.exists(path_scheda):
                    with open(path_scheda, "rb") as f:
                        st.download_button(
                            label=f"⬇️ SCARICA SCHEDA {socio_nome.upper()}",
                            data=f,
                            file_name=os.path.basename(path_scheda),
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
    else:
        st.warning("Aggiungi dei soci nell'anagrafica per abilitare l'export delle schede.")

# ==========================================
# 06. COMPONENTE: MARKETING STUDIO
# ==========================================
def render_marketing_studio():
    st.markdown("<h2 style='color: #0033A0;'>🎨 Marketing Studio</h2>", unsafe_allow_html=True)
    st.markdown("Crea grafiche a 3 fasce come da standard istituzionali.")
    st.divider()

    col_form, col_preview = st.columns([1.2, 1])

    with col_form:
        with st.form("form_banner"):
            st.markdown("#### 1. Testi Principali")
            titolo_evento = st.text_input("Titolo Evento", "ENERGY, INFRASTRUCTURE & INDUSTRIAL SECURITY FORUM")
            sottotitolo = st.text_input("Sottotitolo", "From transit corridor to an integrated platform")
            data_luogo = st.text_input("Data e Luogo", "22 May 2026 | Belgrade")
            
            st.markdown("<br>#### 2. Immagini e Loghi Aggiuntivi", unsafe_allow_html=True)
            c_img1, c_img2 = st.columns(2)
            loghi_org_files = c_img1.file_uploader("Loghi Organizzatori", type=["png", "jpg"], accept_multiple_files=True)
            loghi_part_files = c_img2.file_uploader("Loghi Partner", type=["png", "jpg"], accept_multiple_files=True)
            sfondo_file = st.file_uploader("Grafica di Sfondo", type=["png", "jpg"])
            
            st.markdown("<br>#### 3. Impostazioni Formato", unsafe_allow_html=True)
            formato = st.selectbox("Formato Ottimizzato", ["LinkedIn Banner (1200x627)", "Instagram Post Quadrato (1080x1080)"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted_banner = st.form_submit_button("🚀 COMPONI GRAFICA SOCIAL", type="primary", use_container_width=True)
            
            if submitted_banner:
                from motore.marketing_engine import genera_banner
                conf = leggi_config()
                logo_inst = conf.get('logo_istituzionale', '')
                
                temp_orgs = []
                if loghi_org_files:
                    for i, f in enumerate(loghi_org_files):
                        p = f"exports/temp_org_{i}.{f.name.split('.')[-1]}"
                        with open(p, "wb") as f_out: f_out.write(f.getbuffer())
                        temp_orgs.append(p)
                
                temp_parts = []
                if loghi_part_files:
                    for i, f in enumerate(loghi_part_files):
                        p = f"exports/temp_part_{i}.{f.name.split('.')[-1]}"
                        with open(p, "wb") as f_out: f_out.write(f.getbuffer())
                        temp_parts.append(p)
                        
                temp_sfondo = None
                if sfondo_file:
                    temp_sfondo = f"exports/temp_sfondo.{sfondo_file.name.split('.')[-1]}"
                    with open(temp_sfondo, "wb") as f_out: f_out.write(sfondo_file.getbuffer())
                
                tipo = "linkedin" if "LinkedIn" in formato else "instagram"
                
                with st.spinner("Composizione grafica in corso..."):
                    path_img = genera_banner(
                        titolo_evento, sottotitolo, data_luogo, tipo, 
                        logo_inst=logo_inst, loghi_org=temp_orgs, loghi_partner=temp_parts, sfondo_dx=temp_sfondo
                    )
                    st.session_state['last_banner'] = path_img
                    st.toast("Grafica pronta per il download!", icon="✅")

    with col_preview:
        st.markdown("#### 👁️ Anteprima Risultato")
        if 'last_banner' in st.session_state and os.path.exists(st.session_state['last_banner']):
            st.image(st.session_state['last_banner'], use_container_width=True)
            with open(st.session_state['last_banner'], "rb") as file:
                st.download_button("⬇️ SCARICA IMMAGINE (JPG)", data=file, file_name="Locandina_Assafrica_2026.jpg", mime="image/jpeg", use_container_width=True, type="primary")
        else:
            st.markdown("<div style='height: 350px; display: flex; align-items: center; justify-content: center; background-color: #f0f2f6; border-radius: 10px; color: #888; text-align: center; padding: 20px;'>Compila i dati a sinistra e clicca su 'Componi Grafica' per visualizzare l'anteprima.</div>", unsafe_allow_html=True)

# ==========================================
# 07. COMPONENTE: CONFIGURAZIONE
# ==========================================
def render_configurazione():
    st.markdown("<h2 style='color: #0033A0;'>⚙️ Configurazione Sistema</h2>", unsafe_allow_html=True)
    st.markdown("Gestisci le impostazioni del profilo e i parametri globali dell'applicazione.")
    st.divider()

    # --- PARTE 1: PROFILO E SOCIAL ---
    st.markdown("#### 🏢 Impostazioni Profilo")
    conf = leggi_config()

    with st.form("config_form"):
        col1, col2 = st.columns(2)
        nome_ass = col1.text_input("Nome Associazione", value=conf.get('nome_associazione', 'Assafrica'))
        email_ass = col1.text_input("Email Contatto", value=conf.get('email_contatto', ''))
        indirizzo_ass = col2.text_input("Sede Legale", value=conf.get('indirizzo', ''))
        
        st.markdown("<br>**🌐 Web & Social Media Ufficiali**", unsafe_allow_html=True)
        c_s1, c_s2 = st.columns(2)
        sito_web = c_s1.text_input("Sito Web Ufficiale", value=conf.get('sito_web', 'www.assafrica.it'))
        linkedin = c_s2.text_input("LinkedIn", value=conf.get('linkedin', ''))
        facebook = c_s1.text_input("Facebook", value=conf.get('facebook', ''))
        instagram = c_s2.text_input("Instagram", value=conf.get('instagram', ''))
        youtube = c_s1.text_input("YouTube", value=conf.get('youtube', ''))
        
        st.markdown("<br>**🖼️ Gestione Loghi Istituzionali**", unsafe_allow_html=True)
        c_l1, c_l2 = st.columns(2)
        logo_inst = c_l1.file_uploader("Logo per sfondo CHIARO (Standard)", type=["png", "jpg", "jpeg"])
        logo_neg = c_l2.file_uploader("Logo per sfondo SCURO (Bianco/Negative)", type=["png", "jpg", "jpeg"])
        
        if st.form_submit_button("💾 SALVA PROFILO E SOCIAL", type="primary", use_container_width=True):
            path_std = conf.get('logo_istituzionale', '')
            path_neg = conf.get('logo_negativo', '')
            
            if not os.path.exists("media/loghi_soci"): os.makedirs("media/loghi_soci")
            
            if logo_inst:
                ext_std = logo_inst.name.split('.')[-1].lower()
                path_std = f"media/loghi_soci/LOGO_STD.{ext_std}"
                with open(path_std, "wb") as f:
                    f.write(logo_inst.getbuffer())
            
            if logo_neg:
                ext_neg = logo_neg.name.split('.')[-1].lower()
                path_neg = f"media/loghi_soci/LOGO_NEG.{ext_neg}"
                with open(path_neg, "wb") as f:
                    f.write(logo_neg.getbuffer())
            
            salva_config(nome_ass, path_std, path_neg, indirizzo_ass, email_ass, sito_web, linkedin, facebook, instagram, youtube)
            st.toast("Profilo, Social e loghi salvati correttamente!", icon="✅")
            st.rerun()

    st.divider()

    # --- PARTE 2: SETTORI DINAMICI ---
    st.markdown("#### 🏷️ Gestione Settori Merceologici")
    st.caption("Aggiungi o rimuovi le voci che appariranno nei menu a tendina in tutta l'applicazione.")
    
    categorie_attuali = ottieni_categorie()

    col_add, col_rem = st.columns([1, 1])

    with col_add:
        st.info("**Aggiungi Settore**")
        nuovo_settore = st.text_input("Nome del nuovo settore", placeholder="Es. FARMACEUTICA", label_visibility="collapsed").strip().upper()
        
        if st.button("➕ AGGIUNGI SETTORE", use_container_width=True):
            if nuovo_settore and nuovo_settore not in categorie_attuali:
                categorie_attuali.append(nuovo_settore)
                salva_categorie(sorted(categorie_attuali))
                st.toast(f"Settore '{nuovo_settore}' aggiunto!", icon="✅")
                st.rerun()
            elif nuovo_settore in categorie_attuali:
                st.warning("Questo settore esiste già.")

    with col_rem:
        st.warning("**Rimuovi Settore**")
        if categorie_attuali:
            settore_da_rimuovere = st.selectbox("Seleziona settore da eliminare", categorie_attuali, label_visibility="collapsed")
            if st.button("🗑️ ELIMINA SETTORE", use_container_width=True):
                categorie_attuali.remove(settore_da_rimuovere)
                salva_categorie(categorie_attuali)
                st.toast(f"Settore rimosso!", icon="🗑️")
                st.rerun()

# ==========================================
# 08. COMPONENTE: CENTRO RISORSE (KIT DOCUMENTI)
# ==========================================
def render_risorse():
    st.markdown("<h2 style='color: #0033A0;'>📚 Centro Risorse & Kit Documenti</h2>", unsafe_allow_html=True)
    st.markdown("Accedi ai materiali istituzionali o carica nuovi documenti direttamente nel cloud locale.")
    st.divider()

    base_dir = "risorse"
    cat_dirs = {
        "Primo Contatto": os.path.join(base_dir, "contatto"),
        "Presentazioni & Media": os.path.join(base_dir, "media"),
        "Modulistica Amministrativa": os.path.join(base_dir, "moduli")
    }
    
    for path in cat_dirs.values():
        if not os.path.exists(path):
            os.makedirs(path)

    with st.expander("☁️ Carica un nuovo documento nella libreria", expanded=False):
        c_file, c_cat, c_btn = st.columns([2, 1, 1])
        
        nuovo_file = c_file.file_uploader("Seleziona il file dal tuo Mac", label_visibility="collapsed")
        categoria = c_cat.selectbox("Scegli il raccoglitore", list(cat_dirs.keys()), label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if c_btn.button("💾 SALVA IN ARCHIVIO", type="primary", use_container_width=True):
            if nuovo_file is not None:
                percorso_salvataggio = os.path.join(cat_dirs[categoria], nuovo_file.name)
                with open(percorso_salvataggio, "wb") as f:
                    f.write(nuovo_file.getbuffer())
                st.toast(f"File '{nuovo_file.name}' salvato in {categoria}!", icon="✅")
                st.rerun() 
            else:
                st.warning("⚠️ Seleziona prima un file da caricare.")

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🤝 Kit Primo Contatto")
            file_contatto = os.listdir(cat_dirs["Primo Contatto"])
            file_contatto = [f for f in file_contatto if not f.startswith('.')]
            
            if file_contatto:
                for f in file_contatto:
                    c_t, c_b = st.columns([3, 1])
                    c_t.write(f"📄 {f}")
                    path = os.path.join(cat_dirs["Primo Contatto"], f)
                    with open(path, "rb") as file_data:
                        c_b.download_button("Scarica", file_data, file_name=f, key=f"dl_c_{f}", use_container_width=True)
            else:
                st.caption("Nessun documento presente. Caricalo dal pannello in alto.")

    with col2:
        with st.container(border=True):
            st.markdown("#### 📢 Presentazioni & Media")
            file_media = os.listdir(cat_dirs["Presentazioni & Media"])
            file_media = [f for f in file_media if not f.startswith('.')]
            
            if file_media:
                for f in file_media:
                    c_t, c_b = st.columns([3, 1])
                    c_t.write(f"🎬 {f}")
                    path = os.path.join(cat_dirs["Presentazioni & Media"], f)
                    with open(path, "rb") as file_data:
                        c_b.download_button("Scarica", file_data, file_name=f, key=f"dl_m_{f}", use_container_width=True)
            else:
                st.caption("Nessun documento presente. Caricalo dal pannello in alto.")

    st.write("")
    with st.container(border=True):
        st.markdown("#### 📝 Modulistica Amministrativa")
        file_moduli = os.listdir(cat_dirs["Modulistica Amministrativa"])
        file_moduli = [f for f in file_moduli if not f.startswith('.')]
        
        if file_moduli:
            col_mod = st.columns(3)
            idx = 0
            for f in file_moduli:
                path = os.path.join(cat_dirs["Modulistica Amministrativa"], f)
                with open(path, "rb") as file_data:
                    col_mod[idx % 3].download_button(f"📑 {f}", file_data, file_name=f, key=f"dl_mod_{f}", use_container_width=True)
                idx += 1
        else:
            st.caption("Nessun modulo presente. Caricalo dal pannello in alto.")

# ==========================================
# 10. COMPONENTE: ORGANIZZAZIONE (TEAM, BIGLIETTI E FIRME)
# ==========================================
def render_organizzazione():
    st.markdown("<h2 style='color: #0033A0;'>👔 Team e Organizzazione</h2>", unsafe_allow_html=True)
    st.markdown("Gestisci i membri del team, stampa i biglietti da visita e genera le firme email istituzionali.")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Elenco Team", "➕ Aggiungi Membro", "📇 Biglietti da Visita", "✍️ Firme Email"])

    with tab1:
        st.info("💡 **Tip:** Clicca sulle celle per modificare i dati (es. aggiungere un numero di telefono) e poi clicca su 'Salva Modifiche' in basso.")
        df_team = leggi_team()
        
        if not df_team.empty:
            edited_team = st.data_editor(
                df_team,
                column_config={
                    "id": None,
                    "nome": "Nome",
                    "cognome": "Cognome",
                    "ruolo": "Ruolo / Qualifica",
                    "email": "Email Aziendale",
                    "telefono": "Telefono",
                    "linkedin": st.column_config.LinkColumn("Profilo LinkedIn")
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("💾 SALVA MODIFICHE", type="primary", key="save_team"):
                for _, row in edited_team.iterrows():
                    if pd.notna(row.get('id')):
                        tel = str(row['telefono']) if pd.notna(row.get('telefono')) and str(row['telefono']) != 'nan' else ""
                        lnk = str(row['linkedin']) if pd.notna(row.get('linkedin')) and str(row['linkedin']) != 'nan' else ""
                        
                        aggiorna_membro_team(
                            row['id'], row['nome'], row['cognome'], 
                            row['ruolo'], row['email'], tel, lnk
                        )
                st.toast("Dati del team aggiornati con successo!", icon="✅")
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🗑️ Rimuovi Membro"):
                id_del = st.number_input("ID Membro da rimuovere", step=1, value=0, key="del_team")
                if st.button("ELIMINA MEMBRO"):
                    elimina_membro_team(id_del)
                    st.toast("Membro rimosso dal team.", icon="🗑️")
                    st.rerun()
        else:
            st.info("Nessun membro del team inserito. Vai nella scheda 'Aggiungi Membro'.")

    with tab2:
        with st.form("form_nuovo_membro", clear_on_submit=True):
            st.markdown("#### Dati Anagrafici")
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome *")
            cognome = c2.text_input("Cognome *")
            ruolo = st.text_input("Ruolo / Qualifica (es. Direttore Generale) *")
            
            st.markdown("#### Contatti")
            c3, c4 = st.columns(2)
            email = c3.text_input("Email Aziendale *")
            telefono = c4.text_input("Telefono / Mobile")
            linkedin = st.text_input("URL Profilo LinkedIn")
            
            if st.form_submit_button("💾 SALVA MEMBRO TEAM", type="primary", use_container_width=True):
                if nome and cognome and ruolo and email:
                    aggiungi_membro_team(nome, cognome, ruolo, email, telefono, linkedin)
                    st.toast(f"{nome} {cognome} aggiunto al team!", icon="✅")
                    st.rerun()
                else:
                    st.error("I campi con l'asterisco (*) sono obbligatori.")

    with tab3:
        st.markdown("#### 🖨️ Stampa Biglietto (Formato 85x55 mm)")
        st.write("Seleziona un membro del team per generare il PDF del biglietto da visita.")
        
        df_team = leggi_team()
        
        if not df_team.empty:
            nomi_team = [f"{row['nome']} {row['cognome']}" for _, row in df_team.iterrows()]
            membro_selezionato = st.selectbox("Seleziona Membro per Biglietto", nomi_team, key="sel_biglietto")
            
            if st.button("✨ GENERA PDF BIGLIETTO", type="primary"):
                idx = nomi_team.index(membro_selezionato)
                membro_data = df_team.iloc[idx]
                
                with st.spinner(f"Generazione biglietto e QR Code per {membro_selezionato}..."):
                    from motore.pdf_engine import genera_biglietto_visita
                    conf = leggi_config()
                    try:
                        path_pdf = genera_biglietto_visita(membro_data, conf)
                        st.session_state['last_biglietto'] = path_pdf
                        st.session_state['last_membro_b'] = membro_selezionato
                        st.toast("Biglietto pronto!", icon="✅")
                    except Exception as e:
                        st.error(f"Errore tecnico: {e}")
            
            if 'last_biglietto' in st.session_state and os.path.exists(st.session_state['last_biglietto']):
                if st.session_state.get('last_membro_b') == membro_selezionato:
                    st.success("Il PDF è pronto per la stampa.")
                    with open(st.session_state['last_biglietto'], "rb") as f:
                        st.download_button(
                            label=f"⬇️ SCARICA BIGLIETTO DI {membro_selezionato.upper()}",
                            data=f,
                            file_name=f"Biglietto_{membro_selezionato.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
        else:
            st.warning("Aggiungi prima un membro al team per generare i biglietti.")

    # --- FIRME EMAIL (CONDIZIONI MIGLIORATE) ---
    with tab4:
        st.markdown("#### ✍️ Generatore Firme Email")
        st.write("Genera la firma istituzionale da incollare su Outlook, Apple Mail o Gmail.")
        
        df_team = leggi_team()
        
        if not df_team.empty:
            col_sel, col_opt = st.columns([1, 1])
            nomi_team = [f"{row['nome']} {row['cognome']}" for _, row in df_team.iterrows()]
            membro_firma = col_sel.selectbox("Seleziona Membro per la Firma", nomi_team, key="sel_firma")
            
            usa_sponsor = col_opt.toggle("Aggiungi Loghi Partner/Sponsor in calce")
            
            sponsors_data = []
            if usa_sponsor:
                st.markdown("**Carica i loghi dei Partner (Max 3)**")
                c_sp1, c_sp2, c_sp3 = st.columns(3)
                
                sp1 = c_sp1.file_uploader("Sponsor 1", type=['png', 'jpg'], key="sp1")
                lnk1 = c_sp1.text_input("Link S1 (opzionale)", key="l1") if sp1 else None
                if sp1: sponsors_data.append({"img": sp1, "link": lnk1})
                
                sp2 = c_sp2.file_uploader("Sponsor 2", type=['png', 'jpg'], key="sp2")
                lnk2 = c_sp2.text_input("Link S2 (opzionale)", key="l2") if sp2 else None
                if sp2: sponsors_data.append({"img": sp2, "link": lnk2})
                
                sp3 = c_sp3.file_uploader("Sponsor 3", type=['png', 'jpg'], key="sp3")
                lnk3 = c_sp3.text_input("Link S3 (opzionale)", key="l3") if sp3 else None
                if sp3: sponsors_data.append({"img": sp3, "link": lnk3})

            st.divider()
            
            if st.button("✨ GENERA FIRMA", type="primary", use_container_width=True):
                conf = leggi_config()
                idx = nomi_team.index(membro_firma)
                m_data = df_team.iloc[idx]
                
                def get_base64_of_file(file_path):
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            return base64.b64encode(f.read()).decode()
                    return ""
                
                def get_base64_of_upload(upload_obj):
                    return base64.b64encode(upload_obj.getvalue()).decode()

                # Lettura sicura e pulizia delle variabili
                nome_f = str(m_data.get('nome', '')).strip()
                cognome_f = str(m_data.get('cognome', '')).strip()
                ruolo_f = str(m_data.get('ruolo', '')).strip()
                tel_f = str(m_data.get('telefono', '')).strip()
                
                nome_ass = str(conf.get('nome_associazione', 'ASSAFRICA')).strip().upper()
                indirizzo_ass = str(conf.get('indirizzo', '')).strip()
                sito_ass = str(conf.get('sito_web', '')).strip()

                logo_base64 = get_base64_of_file(conf.get('logo_istituzionale', ''))
                logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="180" style="margin-top:15px; margin-bottom:15px; border:none; display:block;" alt="Logo">' if logo_base64 else ""

                # Costruzione HTML condizionale
                html_firma = '<div style="font-family: Arial, Helvetica, sans-serif; font-size: 11pt; color: #333333; line-height: 1.4;">'
                html_firma += f'<span style="font-size: 12pt;">{nome_f} {cognome_f}</span><br>'
                
                if ruolo_f and ruolo_f.lower() not in ['nan', 'none']:
                    html_firma += f'<span style="color: #555555;">{ruolo_f}</span><br>'
                    
                html_firma += f'<br><strong style="font-size: 11pt;">{nome_ass}</strong><br>'
                
                if indirizzo_ass and indirizzo_ass.lower() not in ['nan', 'none']:
                    html_firma += f'<span style="color: #333333;">{indirizzo_ass}</span><br>'
                
                if tel_f and tel_f.lower() not in ['nan', 'none']:
                    html_firma += f'<span>T: {tel_f}</span><br>'
                
                if sito_ass and sito_ass.lower() not in ['nan', 'none']:
                    clean_sito = sito_ass.replace("http://","").replace("https://","")
                    html_firma += f'<a href="http://{clean_sito}" style="color: #0033A0; text-decoration: underline;">{sito_ass}</a><br>'
                
                html_firma += f"{logo_html}"
                
                # Aggiunta Sponsor
                if sponsors_data:
                    html_firma += '<table style="border-collapse: collapse; margin-top: 10px;"><tr>'
                    for sp in sponsors_data:
                        sp_b64 = get_base64_of_upload(sp['img'])
                        link_href = sp['link'] if sp['link'] else "#"
                        html_firma += f'''
                            <td style="padding-right: 15px; border:none;">
                                <a href="{link_href}" target="_blank">
                                    <img src="data:image/png;base64,{sp_b64}" height="45" style="border:none; display:block;" alt="Sponsor">
                                </a>
                            </td>
                        '''
                    html_firma += '</tr></table>'

                html_firma += "</div>"

                st.success("✅ Firma generata! Seleziona tutto il testo qui sotto (incluso il logo), fai Tasto Destro -> Copia, e incollalo nelle impostazioni firme di Outlook/Mail.")
                
                with st.container(border=True):
                    st.markdown(html_firma, unsafe_allow_html=True)
                    
                with st.expander("Mostra Codice HTML Raw (Per programmatori)"):
                    st.code(html_firma, language='html')

        else:
            st.warning("Aggiungi prima un membro al team.")

# ==========================================
# 09. COMPONENTE: FOOTER BARRA LATERALE
# ==========================================
def render_sidebar_footer():
    st.sidebar.divider()
    
    # Il marchio di fabbrica: Prodotto + Software House
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 12px; margin-bottom: 10px;'>
            <b>ConfDesk Enterprise</b><br>
            Digital Association Management<br>
            <i>v1.0 (Release Candidate)</i><br><br>
            Sviluppato da <b>Il Demiurgo</b>
        </div>
        """, unsafe_allow_html=True
    )
    
# ==========================================
# 11. COMPONENTE: MODULO PUBBLICO DI REGISTRAZIONE
# ==========================================
def render_modulo_pubblico():
    conf = leggi_config()
    nome_ass = conf.get('nome_associazione', 'Assafrica')
    
    st.markdown(f"<h1 style='text-align: center; color: #0033A0;'>{nome_ass}</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Modulo di Richiesta Adesione</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Compila il seguente modulo per sottoporre la tua candidatura alla nostra Business Community.</p>", unsafe_allow_html=True)
    st.divider()

    with st.form("public_registration_form", clear_on_submit=True):
        st.markdown("#### 🏢 Dati Aziendali")
        c1, c2 = st.columns(2)
        nome = c1.text_input("Ragione Sociale *")
        cat = c2.selectbox("Settore Merceologico", ottieni_categorie())
        vol_affari = st.selectbox("Volume d'affari", OPZIONI_FATTURATO)
        
        st.write("") # Spazio vuoto pulito
        st.markdown("#### 👤 Contatti del Referente")
        c3, c4 = st.columns(2)
        ref = c3.text_input("Nome e Cognome Referente *")
        mail = c4.text_input("Email Aziendale *")
        web = st.text_input("Sito Web Ufficiale")
        
        st.write("")
        st.markdown("#### 🌍 Operatività Geografica")
        st.info("In quali paesi africani opera o è interessata ad operare la tua azienda?")
        tutto_continente = st.toggle("Operiamo in tutto il continente (Pan-Africana)")
        paesi_selezionati = ["Tutta l'Africa"] if tutto_continente else st.multiselect(
            "Seleziona Paesi", PAESI_AFRICA
        )
        
        st.write("")
        st.markdown("#### 📝 Presentazione")
        desc = st.text_area("Breve descrizione dell'attività aziendale (max 500 caratteri)", max_chars=500, height=100)
        
        st.write("")
        inviato = st.form_submit_button("🚀 INVIA RICHIESTA DI ADESIONE", type="primary", use_container_width=True)
        
        if inviato:
            if nome and ref and mail and paesi_selezionati:
                stringa_paesi = ",".join(paesi_selezionati)
                
                try:
                    aggiungi_socio(
                        nome, cat, ref, mail, web, desc, "", "", "", 
                        "In attesa", stringa_paesi, vol_affari
                    )
                    st.success(f"🎉 **Richiesta inviata con successo!** Grazie per aver applicato. La segreteria di {nome_ass} ti contatterà a breve all'indirizzo {mail}.")
                    st.balloons()
                except Exception as e:
                    st.error("Si è verificato un errore tecnico. Riprova più tardi.")
            else:
                st.error("⚠️ Attenzione: Compila tutti i campi contrassegnati con l'asterisco (*) e seleziona almeno un Paese.")

# ==========================================
# 12. COMPONENTE: GESTIONE EVENTI (ADMIN)
# ==========================================
def render_gestione_eventi():
    st.markdown("<h2 style='color: #0033A0;'>📅 Gestione Eventi e Iscrizioni</h2>", unsafe_allow_html=True)
    st.markdown("Crea nuovi eventi, ottieni i link di invito e gestisci le liste dei partecipanti.")
    st.divider()

    tab1, tab2 = st.tabs(["🎟️ Prossimi Eventi e Partecipanti", "➕ Crea Nuovo Evento"])

    with tab1:
        df_eventi = leggi_eventi()
        if not df_eventi.empty:
            for _, evento in df_eventi.iterrows():
                with st.expander(f"📌 {evento['data_evento']} | {evento['titolo']} - {evento['luogo']}"):
                    
                    # FIX: Mostra la locandina centrata e rimpicciolita al 50%
                    loc = evento.get('locandina_path')
                    if pd.notna(loc) and str(loc) != "" and os.path.exists(str(loc)):
                        _, col_img, _ = st.columns([1, 2, 1])
                        with col_img:
                            st.image(str(loc), use_container_width=True)

                    st.write(f"**Descrizione:** {evento['descrizione']}")
                    
                    # Link dinamico per l'iscrizione
                    link_pubblico = f"http://localhost:8501/?evento={evento['id']}"
                    st.info(f"🌐 **Link Iscrizione Pubblica:** Copia e invia questo link per raccogliere le registrazioni:\n\n👉 **`{link_pubblico}`**")
                    
                    st.divider()
                    st.markdown("#### 👥 Partecipanti Registrati")
                    df_part = leggi_partecipanti(evento['id'])
                    
                    if not df_part.empty:
                        st.dataframe(df_part[['nome', 'cognome', 'azienda', 'ruolo', 'email', 'data_iscrizione']], hide_index=True, use_container_width=True)
                        
                        # Esporta in CSV
                        csv = df_part.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Esporta Lista (CSV)",
                            data=csv,
                            file_name=f"Partecipanti_{evento['titolo'].replace(' ', '_')}.csv",
                            mime="text/csv",
                            key=f"dl_ev_{evento['id']}"
                        )
                    else:
                        st.caption("Nessun partecipante ancora registrato.")
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Elimina Evento", key=f"del_ev_{evento['id']}"):
                        elimina_evento(evento['id'])
                        st.toast("Evento eliminato.", icon="🗑️")
                        st.rerun()
        else:
            st.info("Nessun evento in programma. Vai nella scheda 'Crea Nuovo Evento'.")

    with tab2:
        with st.form("form_nuovo_evento", clear_on_submit=True):
            st.markdown("#### Dettagli Evento")
            titolo = st.text_input("Titolo dell'Evento *", placeholder="Es. Business Forum 2026")
            c1, c2 = st.columns(2)
            data_ev = c1.date_input("Data Evento", format="DD/MM/YYYY")
            luogo = c2.text_input("Luogo / Piattaforma", placeholder="Es. Roma, Sede Centrale / Zoom")
            desc = st.text_area("Breve descrizione (sarà visibile nel modulo di iscrizione)")
            
            st.write("")
            st.markdown("#### 🖼️ Grafica")
            locandina_file = st.file_uploader("Carica Locandina / Banner (Opzionale)", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("💾 SALVA EVENTO", type="primary", use_container_width=True):
                if titolo:
                    path_locandina = ""
                    
                    # Salvataggio immagine fisica se caricata
                    if locandina_file:
                        if not os.path.exists("media/locandine_eventi"): 
                            os.makedirs("media/locandine_eventi")
                        
                        titolo_sicuro = "".join(x for x in titolo if x.isalnum() or x in " ").replace(' ', '_').upper()
                        est = locandina_file.name.split('.')[-1].lower()
                        import time
                        timestamp = int(time.time())
                        path_locandina = f"media/locandine_eventi/{titolo_sicuro}_{timestamp}.{est}"
                        
                        with open(path_locandina, "wb") as f:
                            f.write(locandina_file.getbuffer())
                            
                    aggiungi_evento(titolo, data_ev.strftime("%d/%m/%Y"), luogo, desc, path_locandina)
                    st.toast("Evento creato con successo!", icon="✅")
                    st.rerun()
                else:
                    st.error("Il titolo dell'evento è obbligatorio.")

# ==========================================
# 13. COMPONENTE: MODULO ISCRIZIONE EVENTO PUBBLICO
# ==========================================
def render_modulo_evento(id_evento):
    df_eventi = leggi_eventi()
    evento_target = df_eventi[df_eventi['id'] == int(id_evento)]
    
    if evento_target.empty:
        st.error("⚠️ Evento non trovato o non più disponibile.")
        return

    evento = evento_target.iloc[0]
    conf = leggi_config()
    nome_ass = conf.get('nome_associazione', 'Assafrica')
    
    # Mostra prima la locandina (se c'è), usando le colonne per centrarla e rimpicciolirla
    loc = evento.get('locandina_path')
    if pd.notna(loc) and str(loc) != "" and os.path.exists(str(loc)):
        # Creiamo 3 colonne: 1/4 vuoto a sx, 2/4 per l'immagine al centro, 1/4 vuoto a dx
        _, col_img, _ = st.columns([1, 2, 1])
        with col_img:
            st.image(str(loc), use_container_width=True)
    else:
        # Se non c'è la locandina, mostra l'header classico di testo
        st.markdown(f"<h1 style='text-align: center; color: #0033A0;'>{nome_ass}</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center;'>Iscrizione: {evento['titolo']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>📅 {evento['data_evento']} | 📍 {evento['luogo']}</p>", unsafe_allow_html=True)
    
    if evento['descrizione']:
        st.markdown(f"<div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;'>{evento['descrizione']}</div>", unsafe_allow_html=True)
    
    st.divider()

    with st.form("form_iscrizione_evento", clear_on_submit=True):
        st.markdown("#### Dati Partecipante")
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome *")
        cognome = c2.text_input("Cognome *")
        
        c3, c4 = st.columns(2)
        azienda = c3.text_input("Azienda/Organizzazione *")
        ruolo = c4.text_input("Ruolo")
        
        email = st.text_input("Email di contatto *")
        
        st.write("")
        if st.form_submit_button("🚀 CONFERMA ISCRIZIONE", type="primary", use_container_width=True):
            if nome and cognome and azienda and email:
                try:
                    aggiungi_partecipante(int(id_evento), nome, cognome, azienda, email, ruolo)
                    st.success(f"🎉 **Iscrizione confermata!** Ti aspettiamo all'evento.")
                    st.balloons()
                except Exception as e:
                    st.error("Errore durante l'iscrizione.")
            else:
                st.error("⚠️ Compila tutti i campi obbligatori (*).")

# ==========================================
# 14. COMPONENTE: UFFICIO STAMPA E MEDIA
# ==========================================
def render_ufficio_stampa():
    st.markdown("<h2 style='color: #0033A0;'>📰 Ufficio Stampa & Media Relations</h2>", unsafe_allow_html=True)
    st.markdown("Gestisci i contatti giornalistici e crea mailing list mirate per l'invio dei comunicati stampa.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🗞️ Rubrica Giornalisti", "➕ Aggiungi Contatto", "📤 Genera Mailing List"])

    with tab1:
        st.info("💡 **Tip:** Modifica i dati direttamente nella tabella e clicca 'Salva Modifiche' in basso.")
        df_giornalisti = leggi_giornalisti()
        
        if not df_giornalisti.empty:
            edited_giornalisti = st.data_editor(
                df_giornalisti,
                column_config={
                    "id": None,
                    "nome": "Nome",
                    "cognome": "Cognome",
                    "testata": "Testata / Agenzia (es. ANSA)",
                    "email": "Email",
                    "telefono": "Telefono",
                    "argomenti": "Tag/Argomenti"
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("💾 SALVA MODIFICHE", type="primary", key="save_media"):
                for _, row in edited_giornalisti.iterrows():
                    if pd.notna(row.get('id')):
                        tel = str(row['telefono']) if pd.notna(row.get('telefono')) and str(row['telefono']) != 'nan' else ""
                        arg = str(row['argomenti']) if pd.notna(row.get('argomenti')) and str(row['argomenti']) != 'nan' else ""
                        aggiorna_giornalista(row['id'], row['nome'], row['cognome'], row['testata'], row['email'], tel, arg)
                st.toast("Rubrica media aggiornata!", icon="✅")
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🗑️ Rimuovi Contatto"):
                id_del = st.number_input("ID Giornalista da rimuovere", step=1, value=0, key="del_media")
                if st.button("ELIMINA CONTATTO"):
                    elimina_giornalista(id_del)
                    st.toast("Contatto rimosso.", icon="🗑️")
                    st.rerun()
        else:
            st.info("Nessun contatto inserito. Vai sulla scheda 'Aggiungi Contatto'.")
    
    with tab2:
        with st.form("form_nuovo_giornalista", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome *")
            cognome = c2.text_input("Cognome *")
            testata = st.text_input("Testata / Agenzia Stampa / TV *", placeholder="Es. Il Sole 24 Ore, ANSA, Rai News")
            
            c3, c4 = st.columns(2)
            email = c3.text_input("Email Diretta *")
            telefono = c4.text_input("Cellulare / Redazione")
            
            argomenti = st.text_input("Tag / Argomenti (Separati da virgola)", placeholder="Es. Energia, Africa, Infrastrutture")
            
            if st.form_submit_button("💾 SALVA CONTATTO", type="primary", use_container_width=True):
                if nome and cognome and testata and email:
                    aggiungi_giornalista(nome, cognome, testata, email, telefono, argomenti)
                    st.toast(f"{nome} {cognome} ({testata}) aggiunto!", icon="✅")
                    st.rerun()
                else:
                    st.error("Compila i campi obbligatori (*)")

    with tab3:
        st.markdown("#### 📧 Estrazione Rapida Email per Comunicati")
        st.write("Filtra i giornalisti per argomento e copia istantaneamente le email da incollare nel campo **Ccn (Copia Conoscenza Nascosta)** del tuo programma di posta.")
        
        df_giornalisti = leggi_giornalisti()
        if not df_giornalisti.empty:
            # Estrazione intelligente dei Tag
            tutti_argomenti = []
            for arg in df_giornalisti['argomenti'].dropna():
                if str(arg) != 'nan':
                    tutti_argomenti.extend([a.strip().title() for a in str(arg).split(',') if a.strip()])
            argomenti_univoci = sorted(list(set(tutti_argomenti)))
            
            col_f1, col_f2 = st.columns(2)
            filtro_testata = col_f1.text_input("Cerca per Testata")
            filtro_argomento = col_f2.multiselect("Filtra per Argomenti/Tag", argomenti_univoci)
            
            df_filtrato = df_giornalisti.copy()
            if filtro_testata:
                df_filtrato = df_filtrato[df_filtrato['testata'].str.contains(filtro_testata, case=False, na=False)]
            if filtro_argomento:
                def check_arg(x):
                    if pd.isna(x) or str(x) == 'nan': return False
                    args_giorn = [a.strip().title() for a in str(x).split(',')]
                    return any(arg in args_giorn for arg in filtro_argomento)
                df_filtrato = df_filtrato[df_filtrato['argomenti'].apply(check_arg)]
                
            st.success(f"Trovati **{len(df_filtrato)}** contatti corrispondenti.")
            
            if not df_filtrato.empty:
                stringa_email = "; ".join(df_filtrato['email'].dropna().tolist())
                st.code(stringa_email, language="text")
                st.caption("Copia questo blocco e incollalo nel campo **Ccn** del tuo client email.")
        else:
            st.warning("Aggiungi dei contatti per usare il generatore di Mailing List.")

# ==========================================
# 15. COMPONENTE: SUPPORTO TECNICO PIATTAFORMA
# ==========================================
def render_supporto_tecnico():
    st.markdown("<h2 style='color: #0033A0;'>🛠️ Supporto Tecnico Piattaforma</h2>", unsafe_allow_html=True)
    st.markdown("Hai riscontrato un bug, hai bisogno di una nuova funzione o di assistenza sull'utilizzo del gestionale? Apri un ticket diretto agli sviluppatori.")
    st.divider()

    tab1, tab2 = st.tabs(["✉️ Apri un Ticket", "📋 Stato delle Richieste"])

    with tab1:
        with st.form("form_ticket_tech", clear_on_submit=True):
            st.markdown("#### Invia Segnalazione")
            c1, c2 = st.columns(2)
            richiedente = c1.text_input("Il tuo Nome / Reparto *")
            email = c2.text_input("La tua Email aziendale *")
            
            oggetto = st.selectbox("Tipo di Richiesta", [
                "🐛 Segnalazione Bug / Errore", 
                "✨ Richiesta Nuova Funzionalità", 
                "❓ Assistenza sull'utilizzo", 
                "Altro"
            ])
            messaggio = st.text_area("Descrivi in dettaglio il problema o la richiesta *", height=150)
            
            if st.form_submit_button("🚀 INVIA AL SUPPORTO TECNICO", type="primary", use_container_width=True):
                if richiedente and email and messaggio:
                    aggiungi_ticket(richiedente, email, oggetto, messaggio)
                    st.success("✅ **Ticket inviato con successo!** Il team tecnico è stato informato e prenderà in carico la richiesta.")
                    st.balloons()
                else:
                    st.error("⚠️ Compila tutti i campi obbligatori (*).")

    with tab2:
        st.markdown("#### Pannello di Controllo Ticket")
        st.write("Qui puoi monitorare le tue richieste e l'Amministratore di Sistema (Tu) può chiuderle quando sono state risolte.")
        
        df_ticket = leggi_ticket()
        if not df_ticket.empty:
            aperti = df_ticket[df_ticket['stato'] == 'Aperto']
            chiusi = df_ticket[df_ticket['stato'] == 'Chiuso']
            
            st.markdown(f"##### 🔴 Ticket in Lavorazione ({len(aperti)})")
            if not aperti.empty:
                for _, t in aperti.iterrows():
                    with st.expander(f"TICKET #{t['id']} | {t['oggetto']} - {t['data_richiesta']}"):
                        st.write(f"**Da:** {t['richiedente']} ({t['email']})")
                        st.info(t['messaggio'])
                        # Tasto per chiudere il ticket (Lo userai tu come Admin)
                        if st.button("✅ Contrassegna come Risolto", key=f"chiudi_{t['id']}", type="primary"):
                            chiudi_ticket(t['id'])
                            st.toast("Ticket risolto!", icon="✅")
                            st.rerun()
            else:
                st.caption("Nessun ticket in sospeso. Il sistema funziona alla perfezione!")
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"##### ⚪ Storico Ticket Risolti ({len(chiusi)})")
            if not chiusi.empty:
                for _, t in chiusi.iterrows():
                    with st.expander(f"Risolto | {t['oggetto']} - {t['data_richiesta']}"):
                        st.write(f"**Da:** {t['richiedente']}")
                        st.caption(t['messaggio'])
                        if st.button("🗑️ Elimina dal database", key=f"del_{t['id']}"):
                            elimina_ticket(t['id'])
                            st.rerun()
            else:
                st.caption("Nessun ticket nello storico.")
        else:
            st.info("Non ci sono ticket nel sistema.")