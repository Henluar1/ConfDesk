import sqlite3
import pandas as pd
import os

DB_PATH = "database_soci.db"

def inizializza_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Creazione Tabella Soci Base
        conn.execute('''CREATE TABLE IF NOT EXISTS soci 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nome TEXT, categoria TEXT, referente TEXT, 
                      email TEXT, sito TEXT, descrizione TEXT, 
                      descrizione_lunga TEXT, logo_path TEXT, 
                      immagine_copertina_path TEXT, pagato TEXT, 
                      sede TEXT, volume_affari TEXT)''')
        
        # Migrazione Sicura: Aggiunta Colonne Extra
        cursor.execute("PRAGMA table_info(soci)")
        colonne_soci = [info[1] for info in cursor.fetchall()]
        
        migrazioni_soci = {
            "descrizione_lunga": "TEXT",
            "immagine_copertina_path": "TEXT",
            "volume_affari": "TEXT" 
        }
        
        for col, dtype in migrazioni_soci.items():
            if col not in colonne_soci:
                conn.execute(f"ALTER TABLE soci ADD COLUMN {col} {dtype}")

        # 2. Creazione Tabella Configurazione Base
        conn.execute('''CREATE TABLE IF NOT EXISTS configurazione 
                     (id INTEGER PRIMARY KEY, 
                      nome_associazione TEXT, 
                      logo_istituzionale TEXT, 
                      indirizzo TEXT, 
                      email_contatto TEXT)''')
        
        # Migrazione Sicura: Aggiunta Social
        cursor.execute("PRAGMA table_info(configurazione)")
        colonne_config = [info[1] for info in cursor.fetchall()]
        
        nuove_colonne_config = [
            "logo_negativo", "sito_web", "linkedin", 
            "facebook", "instagram", "youtube"
        ]
        
        for col in nuove_colonne_config:
            if col not in colonne_config:
                conn.execute(f"ALTER TABLE configurazione ADD COLUMN {col} TEXT")
        
        conn.execute("INSERT OR IGNORE INTO configurazione (id, nome_associazione, sito_web) VALUES (1, 'Assafrica', 'www.assafrica.it')")
        
        # 3. Creazione Tabella Team / Organizzazione
        conn.execute('''CREATE TABLE IF NOT EXISTS team 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nome TEXT, 
                      cognome TEXT, 
                      ruolo TEXT, 
                      email TEXT, 
                      telefono TEXT, 
                      linkedin TEXT)''')

        conn.commit()

# 4. Creazione Tabelle Eventi
        conn.execute('''CREATE TABLE IF NOT EXISTS eventi 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      titolo TEXT, 
                      data_evento TEXT, 
                      luogo TEXT, 
                      descrizione TEXT)''')
                      
        # Migrazione Sicura: Aggiunta Locandina
        cursor.execute("PRAGMA table_info(eventi)")
        colonne_eventi = [info[1] for info in cursor.fetchall()]
        if "locandina_path" not in colonne_eventi:
            conn.execute("ALTER TABLE eventi ADD COLUMN locandina_path TEXT")
                      
        conn.execute('''CREATE TABLE IF NOT EXISTS partecipanti_eventi 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      id_evento INTEGER,
                      nome TEXT, 
                      cognome TEXT, 
                      azienda TEXT, 
                      email TEXT, 
                      ruolo TEXT,
                      data_iscrizione TEXT)''')

# 5. Creazione Tabella Ufficio Stampa
        conn.execute('''CREATE TABLE IF NOT EXISTS giornalisti 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nome TEXT, 
                      cognome TEXT, 
                      testata TEXT, 
                      email TEXT, 
                      telefono TEXT, 
                      argomenti TEXT)''')

# 6. Creazione Tabella Supporto Tecnico
        conn.execute('''CREATE TABLE IF NOT EXISTS helpdesk 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      richiedente TEXT, 
                      email TEXT, 
                      oggetto TEXT, 
                      messaggio TEXT, 
                      stato TEXT,
                      data_richiesta TEXT)''')        
        
# --- FUNZIONI CONFIGURAZIONE ---

def salva_config(nome, logo_std, logo_neg, indirizzo, email, sito_web, linkedin, facebook, instagram, youtube):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE configurazione SET 
                     nome_associazione=?, logo_istituzionale=?, logo_negativo=?, indirizzo=?, email_contatto=?,
                     sito_web=?, linkedin=?, facebook=?, instagram=?, youtube=?
                     WHERE id=1""", 
                     (nome, logo_std, logo_neg, indirizzo, email, sito_web, linkedin, facebook, instagram, youtube))
        conn.commit()

def leggi_config():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        res = conn.execute("SELECT * FROM configurazione WHERE id=1").fetchone()
        return dict(res) if res else {}

# --- FUNZIONI SOCI ---

def leggi_soci():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM soci", conn)

def aggiungi_socio(nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO soci (nome, categoria, referente, email, sito, descrizione, descrizione_lunga, logo_path, immagine_copertina_path, pagato, sede, volume_affari) 
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", 
                     (nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari))
        conn.commit()

def aggiorna_socio(id_socio, nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE soci SET 
                     nome=?, categoria=?, referente=?, email=?, sito=?, descrizione=?, descrizione_lunga=?, logo_path=?, immagine_copertina_path=?, pagato=?, sede=?, volume_affari=? 
                     WHERE id=?""", 
                     (nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari, id_socio))
        conn.commit()

def elimina_socio(id_socio):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM soci WHERE id = ?", (id_socio,))
        conn.commit()

# --- FUNZIONI TEAM E ORGANIZZAZIONE ---

def leggi_team():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM team", conn)

def aggiungi_membro_team(nome, cognome, ruolo, email, telefono, linkedin):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO team (nome, cognome, ruolo, email, telefono, linkedin) 
                     VALUES (?, ?, ?, ?, ?, ?)""", 
                     (nome, cognome, ruolo, email, telefono, linkedin))
        conn.commit()

def elimina_membro_team(id_membro):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM team WHERE id = ?", (id_membro,))
        conn.commit()
        
def aggiorna_membro_team(id_membro, nome, cognome, ruolo, email, telefono, linkedin):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE team SET 
                     nome=?, cognome=?, ruolo=?, email=?, telefono=?, linkedin=? 
                     WHERE id=?""", 
                     (nome, cognome, ruolo, email, telefono, linkedin, id_membro))
        conn.commit()  

# --- FUNZIONI EVENTI E PARTECIPANTI ---
def leggi_eventi():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM eventi ORDER BY id DESC", conn)

def aggiungi_evento(titolo, data_evento, luogo, descrizione, locandina_path=""):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO eventi (titolo, data_evento, luogo, descrizione, locandina_path) VALUES (?, ?, ?, ?, ?)", 
                     (titolo, data_evento, luogo, descrizione, locandina_path))
        conn.commit()

def elimina_evento(id_evento):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM eventi WHERE id = ?", (id_evento,))
        conn.execute("DELETE FROM partecipanti_eventi WHERE id_evento = ?", (id_evento,))
        conn.commit()

def leggi_partecipanti(id_evento):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM partecipanti_eventi WHERE id_evento = ?", conn, params=(id_evento,))

def aggiungi_partecipante(id_evento, nome, cognome, azienda, email, ruolo):
    import datetime
    oggi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO partecipanti_eventi 
                     (id_evento, nome, cognome, azienda, email, ruolo, data_iscrizione) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                     (id_evento, nome, cognome, azienda, email, ruolo, oggi))
        conn.commit()      

# --- FUNZIONI UFFICIO STAMPA ---
def leggi_giornalisti():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM giornalisti ORDER BY testata, cognome", conn)

def aggiungi_giornalista(nome, cognome, testata, email, telefono, argomenti):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO giornalisti (nome, cognome, testata, email, telefono, argomenti) VALUES (?, ?, ?, ?, ?, ?)", 
                     (nome, cognome, testata, email, telefono, argomenti))
        conn.commit()

def aggiorna_giornalista(id_g, nome, cognome, testata, email, telefono, argomenti):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE giornalisti SET nome=?, cognome=?, testata=?, email=?, telefono=?, argomenti=? WHERE id=?", 
                     (nome, cognome, testata, email, telefono, argomenti, id_g))
        conn.commit()

def elimina_giornalista(id_g):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM giornalisti WHERE id = ?", (id_g,))
        conn.commit()

# --- FUNZIONI HELPDESK / SUPPORTO IT ---
def leggi_ticket():
    with sqlite3.connect(DB_PATH) as conn:
        # Ordina mostrando prima i ticket Aperti, poi quelli Chiusi, e i più recenti in alto
        return pd.read_sql_query("SELECT * FROM helpdesk ORDER BY CASE WHEN stato='Aperto' THEN 1 ELSE 2 END, id DESC", conn)

def aggiungi_ticket(richiedente, email, oggetto, messaggio):
    import datetime
    oggi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO helpdesk (richiedente, email, oggetto, messaggio, stato, data_richiesta) VALUES (?, ?, ?, ?, 'Aperto', ?)", 
                     (richiedente, email, oggetto, messaggio, oggi))
        conn.commit()

def chiudi_ticket(id_ticket):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE helpdesk SET stato='Chiuso' WHERE id=?", (id_ticket,))
        conn.commit()
        
def elimina_ticket(id_ticket):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM helpdesk WHERE id=?", (id_ticket,))
        conn.commit()