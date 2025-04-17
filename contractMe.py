"""
# ContractME - Piattaforma di gestione documenti personali
# -----------------------------------------------------
# Come eseguire la demo:
# 1. Assicurati di avere Python installato
# 2. Installa le dipendenze: pip install streamlit pandas matplotlib pillow python-docx PyPDF2
# 3. Salva questo file come 'app.py'
# 4. Esegui: streamlit run app.py
# -----------------------------------------------------
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import base64
import datetime
import random
import tempfile
from PIL import Image
import PyPDF2
import time
from datetime import datetime, timedelta

# Configurazione pagina
st.set_page_config(
    page_title="ContractME - Gestione Documenti",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stili CSS personalizzati
st.markdown("""
<style>
    .main-header {
        font-size: 30px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 20px;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .card {
        padding: 20px;
        border-radius: 5px;
        background-color: #F3F4F6;
        margin-bottom: 20px;
    }
    .highlight {
        color: #1E3A8A;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #6B7280;
        font-size: 14px;
    }
    .sidebar-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 30px;
    }
    .expiry-alert {
        color: #DC2626;
        font-weight: bold;
    }
    .success-text {
        color: #059669;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inizializzazione stato sessione
def init_session_state():
    # Documenti
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    
    # Categorie documenti
    if 'categories' not in st.session_state:
        st.session_state.categories = ["Casa", "Lavoro", "Viaggi", "Salute", "Finanze", "Altro"]
    
    # Scadenze
    if 'deadlines' not in st.session_state:
        # Genera alcune scadenze di esempio
        today = datetime.now()
        st.session_state.deadlines = [
            {"title": "Rinnovo contratto affitto", "date": today + timedelta(days=15), "category": "Casa", "description": "Contattare proprietario per rinnovo", "document_id": None},
            {"title": "Pagamento bolletta energia", "date": today + timedelta(days=7), "category": "Casa", "description": "Scadenza bolletta ultimo bimestre", "document_id": None},
            {"title": "Visita medica annuale", "date": today + timedelta(days=30), "category": "Salute", "description": "Prenotare visita di controllo", "document_id": None}
        ]
    
    # Ultima chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Documento selezionato per AI
    if 'selected_doc_for_ai' not in st.session_state:
        st.session_state.selected_doc_for_ai = None
    
    # Piano di abbonamento (simulato)
    if 'subscription' not in st.session_state:
        st.session_state.subscription = {"plan": "Premium", "expiry": datetime.now() + timedelta(days=30)}

# Funzioni di utilità per la gestione dei documenti
def save_uploaded_file(uploaded_file):
    """Salva il file caricato temporaneamente e restituisce il percorso"""
    try:
        # Crea una directory temporanea se non esiste
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Errore nel salvataggio del file: {e}")
        return None

def extract_text_from_pdf(file_path):
    """Estrae il testo da un file PDF"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Errore nell'estrazione del testo dal PDF: {e}")
        return "Non è stato possibile estrarre il testo da questo PDF."

def get_file_preview(file_path):
    """Genera un'anteprima del file in base al tipo"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        # Estrai solo la prima pagina del PDF
        text = extract_text_from_pdf(file_path)
        return text[:500] + "..." if len(text) > 500 else text
    
    elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
        try:
            return Image.open(file_path)
        except Exception as e:
            return f"Non è stato possibile visualizzare l'immagine: {e}"
    
    elif file_ext in ['.txt', '.md']:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content[:500] + "..." if len(content) > 500 else content
        except Exception as e:
            return f"Non è stato possibile leggere il file: {e}"
    
    else:
        return "Anteprima non disponibile per questo tipo di file."

def get_file_content(file_path):
    """Recupera il contenuto completo del file"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    
    elif file_ext in ['.txt', '.md']:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Non è stato possibile leggere il file: {e}"
    
    else:
        return "Contenuto non disponibile per questo tipo di file."

def simulate_ai_response(query, document_content):
    """Simula una risposta dell'AI basata sul documento selezionato"""
    # Semplice simulazione di una risposta basata sul contenuto del documento
    ai_responses = [
        f"Analizzando il documento, ho trovato informazioni relative alla tua domanda '{query}'. Nel documento si menziona che...",
        f"Basandomi sul contenuto del documento, posso rispondere che il tuo quesito '{query}' è collegato a...",
        f"Ho esaminato il documento e in risposta a '{query}', posso dirti che...",
        f"La tua domanda '{query}' è interessante. Dal documento emerge che...",
        f"Ho analizzato il testo e per quanto riguarda '{query}', il documento indica che..."
    ]
    
    # Genera un piccolo estratto dal documento
    words = document_content.split()
    if len(words) > 20:
        excerpt = " ".join(random.sample(words, min(20, len(words))))
    else:
        excerpt = document_content
    
    response = random.choice(ai_responses)
    return response + f" '{excerpt}...'"

def get_chart_category_distribution():
    """Genera un grafico per la distribuzione dei documenti per categoria"""
    # Conta documenti per categoria
    categories = {}
    for doc in st.session_state.documents:
        cat = doc['category']
        if cat in categories:
            categories[cat] += 1
        else:
            categories[cat] = 1
    
    # Crea il grafico
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Se non ci sono documenti, mostra un messaggio
    if not categories:
        ax.text(0.5, 0.5, "Nessun documento caricato", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.axis('off')
        return fig
    
    bars = ax.bar(categories.keys(), categories.values(), color='#1E3A8A')
    
    # Aggiungi etichette
    ax.set_xlabel('Categoria')
    ax.set_ylabel('Numero di documenti')
    ax.set_title('Distribuzione dei documenti per categoria')
    
    # Aggiungi i valori sopra le barre
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 punti di offset verticale
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig

def get_deadlines_chart():
    """Genera un grafico per le scadenze prossime"""
    # Ordina le scadenze per data
    deadlines = sorted(st.session_state.deadlines, key=lambda x: x['date'])
    
    # Prendi solo le prossime 5 scadenze
    next_deadlines = deadlines[:5]
    
    # Crea il grafico
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Se non ci sono scadenze, mostra un messaggio
    if not next_deadlines:
        ax.text(0.5, 0.5, "Nessuna scadenza programmata", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.axis('off')
        return fig
    
    # Prepara i dati per il grafico
    titles = [d['title'] for d in next_deadlines]
    dates = [d['date'] for d in next_deadlines]
    today = datetime.now()
    days_remaining = [(d - today).days for d in dates]
    
    # Colori in base all'urgenza
    colors = ['#DC2626' if days <= 7 else '#F59E0B' if days <= 14 else '#059669' for days in days_remaining]
    
    # Crea il grafico a barre orizzontale
    bars = ax.barh(titles, days_remaining, color=colors)
    
    # Aggiungi etichette
    ax.set_xlabel('Giorni rimanenti')
    ax.set_title('Prossime scadenze')
    
    # Aggiungi i valori accanto alle barre
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width
        ax.text(label_x_pos + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)} giorni',
                va='center')
    
    plt.tight_layout()
    
    return fig

# Componenti dell'interfaccia utente
def render_header():
    """Mostra l'intestazione dell'app"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">ContractME</div>', unsafe_allow_html=True)
        st.markdown("Piattaforma di gestione documenti personali e contratti")
    
    with col2:
        expiry_date = st.session_state.subscription["expiry"]
        days_left = (expiry_date - datetime.now()).days
        
        st.markdown(f"""
        <div class="card">
            <div>Piano: <span class="highlight">{st.session_state.subscription["plan"]}</span></div>
            <div>Scadenza: <span class="{'expiry-alert' if days_left < 10 else ''}">{expiry_date.strftime('%d/%m/%Y')} ({days_left} giorni)</span></div>
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """Mostra la sidebar con le opzioni di navigazione"""
    st.sidebar.markdown('<div class="sidebar-header">ContractME</div>', unsafe_allow_html=True)
    
    # Menu di navigazione
    page = st.sidebar.radio("Naviga", ["Dashboard", "Carica Documento", "Assistente AI", "Scadenze e Calendario"])
    
    # Informazioni sull'utente
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div>
        <p><b>Account:</b> Premium</p>
        <p><b>Documenti:</b> {len(st.session_state.documents)}/100</p>
        <p><b>Spazio utilizzato:</b> {random.randint(10, 90)}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer della sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="footer">
        © 2025 ContractME<br>
        Versione Demo
    </div>
    """, unsafe_allow_html=True)
    
    return page

def render_dashboard():
    """Mostra la dashboard con statistiche e panoramica"""
    st.markdown('<div class="sub-header">Dashboard</div>', unsafe_allow_html=True)
    
    # Statistiche principali
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Documenti Totali", value=len(st.session_state.documents))
    with col2:
        # Calcola il numero di documenti caricati negli ultimi 7 giorni
        recent_docs = sum(1 for doc in st.session_state.documents if (datetime.now() - doc['upload_date']).days <= 7)
        st.metric(label="Caricati Recentemente", value=recent_docs)
    with col3:
        # Conta le categorie utilizzate
        used_categories = len(set(doc['category'] for doc in st.session_state.documents))
        st.metric(label="Categorie Utilizzate", value=used_categories)
    with col4:
        # Calcola le scadenze imminenti (entro 7 giorni)
        upcoming = sum(1 for d in st.session_state.deadlines if (d['date'] - datetime.now()).days <= 7)
        st.metric(label="Scadenze Imminenti", value=upcoming)
    
    # Grafico distribuzione documenti per categoria
    st.markdown('<div class="sub-header">Distribuzione dei documenti</div>', unsafe_allow_html=True)
    category_chart = get_chart_category_distribution()
    st.pyplot(category_chart)
    
    # Scadenze prossime
    st.markdown('<div class="sub-header">Prossime scadenze</div>', unsafe_allow_html=True)
    deadlines_chart = get_deadlines_chart()
    st.pyplot(deadlines_chart)
    
    # Documenti recenti
    st.markdown('<div class="sub-header">Documenti recenti</div>', unsafe_allow_html=True)
    
    if not st.session_state.documents:
        st.info("Non hai ancora caricato documenti. Vai alla sezione 'Carica Documento' per iniziare.")
    else:
        # Ordina i documenti per data di caricamento (più recente prima)
        recent_documents = sorted(st.session_state.documents, key=lambda x: x['upload_date'], reverse=True)[:5]
        
        # Mostra i documenti recenti
        for doc in recent_documents:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="card">
                    <strong>{doc['name']}</strong> <span style="color: #6B7280;">({doc['category']})</span><br>
                    <small>Caricato il {doc['upload_date'].strftime('%d/%m/%Y %H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.button("Visualizza", key=f"view_{doc['id']}", 
                          help=f"Visualizza {doc['name']}")

def render_upload_document():
    """Mostra la pagina di caricamento dei documenti"""
    st.markdown('<div class="sub-header">Carica un nuovo documento</div>', unsafe_allow_html=True)
    
    # Form di caricamento
    with st.form("upload_form"):
        uploaded_file = st.file_uploader("Seleziona un file da caricare", 
                                        type=['pdf', 'txt', 'jpg', 'jpeg', 'png'])
        
        doc_name = st.text_input("Nome del documento (opzionale)")
        
        category = st.selectbox("Categoria", options=st.session_state.categories)
        
        has_deadline = st.checkbox("Il documento ha una scadenza?")
        
        deadline_date = None
        deadline_description = ""
        
        if has_deadline:
            deadline_date = st.date_input("Data scadenza", 
                                         min_value=datetime.now().date(),
                                         value=(datetime.now() + timedelta(days=30)).date())
            
            deadline_description = st.text_input("Descrizione scadenza")
        
        submit_button = st.form_submit_button("Carica documento")
        
        if submit_button and uploaded_file is not None:
            # Salva il file
            file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                # Se non è stato fornito un nome, usa il nome del file
                if not doc_name:
                    doc_name = uploaded_file.name
                
                # Genera un ID univoco
                doc_id = f"doc_{len(st.session_state.documents) + 1}_{int(time.time())}"
                
                # Aggiungi il documento alla collezione
                doc = {
                    "id": doc_id,
                    "name": doc_name,
                    "path": file_path,
                    "category": category,
                    "upload_date": datetime.now(),
                    "type": uploaded_file.type,
                    "size": uploaded_file.size
                }
                
                st.session_state.documents.append(doc)
                
                # Se il documento ha una scadenza, aggiungi anche quella
                if has_deadline and deadline_date:
                    deadline = {
                        "title": f"Scadenza: {doc_name}",
                        "date": datetime.combine(deadline_date, datetime.min.time()),
                        "category": category,
                        "description": deadline_description,
                        "document_id": doc_id
                    }
                    
                    st.session_state.deadlines.append(deadline)
                
                st.success(f"Documento '{doc_name}' caricato con successo!")
                
                # Mostra l'anteprima
                st.markdown('<div class="sub-header">Anteprima documento</div>', unsafe_allow_html=True)
                
                preview = get_file_preview(file_path)
                
                if isinstance(preview, Image.Image):
                    st.image(preview, caption=doc_name)
                else:
                    st.text_area("Contenuto:", value=preview, height=300, disabled=True)
    
    # Lista documenti caricati
    st.markdown('<div class="sub-header">Documenti caricati</div>', unsafe_allow_html=True)
    
    if not st.session_state.documents:
        st.info("Non hai ancora caricato documenti.")
    else:
        # Opzioni di filtraggio
        filter_category = st.selectbox("Filtra per categoria", 
                                     options=["Tutte"] + st.session_state.categories)
        
        # Filtra i documenti
        filtered_docs = st.session_state.documents
        if filter_category != "Tutte":
            filtered_docs = [doc for doc in st.session_state.documents if doc['category'] == filter_category]
        
        # Mostra i documenti filtrati
        for doc in filtered_docs:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <strong>{doc['name']}</strong> <span style="color: #6B7280;">({doc['category']})</span><br>
                    <small>Caricato il {doc['upload_date'].strftime('%d/%m/%Y %H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("Visualizza", key=f"view_{doc['id']}"):
                    # Mostra un dialogo con l'anteprima del documento
                    st.session_state.preview_doc = doc
            
            with col3:
                if st.button("Elimina", key=f"delete_{doc['id']}"):
                    # Rimuovi il documento
                    st.session_state.documents.remove(doc)
                    
                    # Rimuovi anche le scadenze associate
                    st.session_state.deadlines = [d for d in st.session_state.deadlines if d['document_id'] != doc['id']]
                    
                    st.experimental_rerun()
    
    # Mostra l'anteprima se un documento è stato selezionato
    if hasattr(st.session_state, 'preview_doc') and st.session_state.preview_doc:
        doc = st.session_state.preview_doc
        
        st.markdown('<div class="sub-header">Anteprima documento</div>', unsafe_allow_html=True)
        
        # Mostra i dettagli del documento
        st.markdown(f"""
        <div class="card">
            <strong>{doc['name']}</strong><br>
            <small>Categoria: {doc['category']}</small><br>
            <small>Caricato il: {doc['upload_date'].strftime('%d/%m/%Y %H:%M')}</small><br>
            <small>Tipo: {doc['type']}</small><br>
            <small>Dimensione: {doc['size'] / 1024:.1f} KB</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostra l'anteprima
        preview = get_file_preview(doc['path'])
        
        if isinstance(preview, Image.Image):
            st.image(preview, caption=doc['name'])
        else:
            st.text_area("Contenuto:", value=preview, height=300, disabled=True)
        
        # Pulsante per chiudere l'anteprima
        if st.button("Chiudi anteprima"):
            del st.session_state.preview_doc
            st.experimental_rerun()

def render_ai_assistant():
    """Mostra la pagina dell'assistente AI"""
    st.markdown('<div class="sub-header">Assistente AI ContractME</div>', unsafe_allow_html=True)
    
    # Selezione del documento
    if not st.session_state.documents:
        st.info("Non hai ancora caricato documenti. Vai alla sezione 'Carica Documento' per iniziare.")
        return
    
    # Opzioni per il documento
    doc_options = {doc['name']: doc for doc in st.session_state.documents}
    selected_doc_name = st.selectbox("Seleziona un documento", options=list(doc_options.keys()))
    
    # Aggiorna il documento selezionato
    selected_doc = doc_options[selected_doc_name]
    st.session_state.selected_doc_for_ai = selected_doc
    
    # Mostra i dettagli del documento
    st.markdown(f"""
    <div class="card">
        <strong>{selected_doc['name']}</strong><br>
        <small>Categoria: {selected_doc['category']}</small><br>
        <small>Caricato il: {selected_doc['upload_date'].strftime('%d/%m/%Y %H:%M')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Area di chat
    st.markdown('<div class="sub-header">Chat con l\'assistente</div>', unsafe_allow_html=True)
    
    # Mostra la cronologia della chat
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                <div style="background-color: #E0E7FF; padding: 10px; border-radius: 10px; max-width: 70%;">
                    <strong>Tu:</strong><br>{message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                <div style="background-color: #F3F4F6; padding: 10px; border-radius: 10px; max-width: 70%;">
                    <strong>Assistente:</strong><br>{message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Input per la domanda
    with st.form("chat_form"):
        query = st.text_input("Fai una domanda sul documento", placeholder="Ad esempio: quali sono le scadenze previste?")
        
        submit_query = st.form_submit_button("Invia")
        
        if submit_query and query:
            # Recupera il contenuto del documento
            doc_content = get_file_content(selected_doc['path'])
            
            # Simula una risposta dell'AI
            ai_response = simulate_ai_response(query, doc_content)
            
            # Aggiungi la domanda e la risposta alla cronologia
            st.session_state.chat_history.append({"role": "user", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Aggiorna la pagina
            st.experimental_rerun()
    
    # Pulsante per cancellare la cronologia
    if st.session_state.chat_history and st.button("Cancella cronologia"):
        st.session_state.chat_history = []
        st.experimental_rerun()

def render_deadlines():
    """Mostra la pagina delle scadenze e del calendario"""
    st.markdown('<div class="sub-header">Scadenze e Calendario</div>', unsafe_allow_html=True)
    
    # Schede per scadenze e calendario
    tab1, tab2 = st.tabs(["Lista Scadenze", "Calendario"])
    
    with tab1:
        # Aggiungi nuova scadenza
        with st.expander("Aggiungi nuova scadenza"):
            with st.form("new_deadline_form"):
                title = st.text_input("Titolo", placeholder="Ad esempio: Rinnovo patente")
                
                deadline_date = st.date_input("Data scadenza", 
                                            min_value=datetime.now().date(),
                                            value=(datetime.now() + timedelta(days=30)).date())
                
                category = st.selectbox("Categoria", options=st.session_state.categories)
                
                description = st.text_area("Descrizione", placeholder="Inserisci dettagli aggiuntivi...")
                
                # Opzione per collegare a un documento esistente
                link_to_doc = st.checkbox("Collega a un documento esistente")
                doc_id = None
                
                if link_to_doc and st.session_state.documents:
                    doc_options = {doc['name']: doc['id'] for doc in st.session_state.documents}
                    selected_doc = st.selectbox("Seleziona documento", options=list(doc_options.keys()))
                    doc_id = doc_options[selected_doc]
                
                submit_deadline = st.form_submit_button("Salva scadenza")
                
                if submit_deadline and title:
                    # Aggiungi la scadenza
                    new_deadline = {
                        "title": title,
                        "date": datetime.combine(deadline_date, datetime.min.time()),
                        "category": category,
                        "description": description,
                        "document_id": doc_id
                    }
                    
                    st.session_state.deadlines.append(new_deadline)
                    st.success("Scadenza aggiunta con successo!")
                    st.experimental_rerun()
        
        # Lista delle scadenze
        if not st.session_state.deadlines:
            st.info("Non hai ancora impostato scadenze.")
        else:
            # Filtro per categoria
            filter_cat = st.selectbox("Filtra per categoria", 
                                     options=["Tutte"] + st.session_state.categories,
                                     key="deadline_filter")
            
            # Ordina le scadenze per data
            sorted_deadlines = sorted(st.session_state.deadlines, key=lambda x: x['date'])
            
            # Filtra le scadenze
            if filter_cat != "Tutte":
                sorted_deadlines = [d for d in sorted_deadlines if d['category'] == filter_cat]
            
            # Mostra le scadenze
            for deadline in sorted_deadlines:
                days_left = (deadline['date'] - datetime.now()).days
                is_urgent = days_left <= 7
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <strong>{deadline['title']}</strong> <span style="color: #6B7280;">({deadline['category']})</span><br>
                        <small>Scadenza: <span class="{'expiry-alert' if is_urgent else ''}">{deadline['date'].strftime('%d/%m/%Y')} ({days_left} giorni)</span></small><br>
                        <small>{deadline['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Se la scadenza è collegata a un documento, mostra un pulsante per visualizzarlo
                    if deadline['document_id']:
                        # Trova il documento collegato
                        linked_doc = next((doc for doc in st.session_state.documents if doc['id'] == deadline['document_id']), None)
                        
                        if linked_doc:
                            if st.button("Documento", key=f"doc_{deadline['title']}"):
                                st.session_state.preview_doc = linked_doc
                                st.experimental_rerun()
                
                with col3:
                    if st.button("Elimina", key=f"del_{deadline['title']}"):
                        st.session_state.deadlines.remove(deadline)
                        st.experimental_rerun()
    
    with tab2:
        st.markdown("""
        <div style="text-align: center;">
            <h2 style="color: #1E3A8A;">Calendario Scadenze</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Ottieni il mese corrente
        today = datetime.now()
        current_month = today.month
        current_year = today.year
        
        # Selezione del mese
        months = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                 "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_month = st.selectbox("Mese", options=months, index=current_month-1)
            month_num = months.index(selected_month) + 1
        
        with col2:
            selected_year = st.selectbox("Anno", options=range(current_year, current_year+5), index=0)
        
        # Crea il calendario
        # Ottenere il primo giorno del mese e il numero di giorni nel mese
        first_day = datetime(selected_year, month_num, 1)
        if month_num == 12:
            last_day = datetime(selected_year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(selected_year, month_num + 1, 1) - timedelta(days=1)
        
        num_days = last_day.day
        
        # Trova il giorno della settimana del primo giorno (0 = lunedì, 6 = domenica)
        first_weekday = first_day.weekday()
        
        # Crea una matrice per il calendario
        calendar_matrix = []
        day = 1
        
        # Intestazione giorni della settimana
        week_days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
        
        # Crea il calendario HTML
        calendar_html = f"""
        <div style="margin: 20px auto; max-width: 800px;">
            <table style="width: 100%; border-collapse: collapse; text-align: center;">
                <tr>
        """
        
        # Aggiungi intestazioni giorni
        for day_name in week_days:
            calendar_html += f"<th style='padding: 10px; background-color: #1E3A8A; color: white;'>{day_name}</th>"
        
        calendar_html += "</tr>"
        
        # Riempi il calendario
        # Aggiungi celle vuote fino al primo giorno del mese
        calendar_html += "<tr>"
        for i in range(first_weekday):
            calendar_html += "<td style='padding: 10px; border: 1px solid #E5E7EB;'></td>"
        
        # Scadenze per questo mese
        month_deadlines = [d for d in st.session_state.deadlines 
                          if d['date'].month == month_num and d['date'].year == selected_year]
        
        # Mappa delle scadenze per giorno
        deadlines_by_day = {}
        for d in month_deadlines:
            day_num = d['date'].day
            if day_num not in deadlines_by_day:
                deadlines_by_day[day_num] = []
            deadlines_by_day[day_num].append(d)
        
        # Riempi i giorni del mese
        current_weekday = first_weekday
        for day_num in range(1, num_days + 1):
            # Controlla se è oggi
            is_today = (day_num == today.day and month_num == today.month and selected_year == today.year)
            
            # Controlla se ci sono scadenze per questo giorno
            has_deadlines = day_num in deadlines_by_day
            
            # Stile della cella
            cell_style = "padding: 10px; border: 1px solid #E5E7EB;"
            if is_today:
                cell_style += "background-color: #E0E7FF; font-weight: bold;"
            elif has_deadlines:
                cell_style += "background-color: #FEF3C7;"
            
            # Contenuto della cella
            cell_content = f"{day_num}"
            if has_deadlines:
                deadline_count = len(deadlines_by_day[day_num])
                cell_content += f"<br><small style='color: #DC2626;'>{deadline_count} scad.</small>"
            
            calendar_html += f"<td style='{cell_style}'>{cell_content}</td>"
            
            # Vai alla riga successiva se è domenica
            current_weekday = (current_weekday + 1) % 7
            if current_weekday == 0 and day_num < num_days:
                calendar_html += "</tr><tr>"
        
        # Aggiungi celle vuote alla fine se necessario
        if current_weekday > 0:
            for i in range(7 - current_weekday):
                calendar_html += "<td style='padding: 10px; border: 1px solid #E5E7EB;'></td>"
        
        calendar_html += "</tr></table></div>"
        
        # Mostra il calendario
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        # Mostra le scadenze del mese selezionato
        if month_deadlines:
            st.markdown(f"<h3>Scadenze di {selected_month} {selected_year}</h3>", unsafe_allow_html=True)
            
            # Ordina le scadenze per giorno
            month_deadlines.sort(key=lambda x: x['date'].day)
            
            for deadline in month_deadlines:
                day_num = deadline['date'].day
                days_left = (deadline['date'] - datetime.now()).days
                is_urgent = days_left <= 7
                
                st.markdown(f"""
                <div class="card">
                    <strong>{deadline['title']}</strong> - Giorno {day_num}<br>
                    <small>Categoria: {deadline['category']}</small><br>
                    <small>Giorni rimanenti: <span class="{'expiry-alert' if is_urgent else ''}">{days_left}</span></small><br>
                    <small>{deadline['description']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"Non ci sono scadenze programmate per {selected_month} {selected_year}.")

def main():
    """Funzione principale dell'applicazione"""
    # Inizializza lo stato della sessione
    init_session_state()
    
    # Mostra l'intestazione
    render_header()
    
    # Mostra la sidebar e ottieni la pagina selezionata
    page = render_sidebar()
    
    # Mostra la pagina selezionata
    if page == "Dashboard":
        render_dashboard()
    elif page == "Carica Documento":
        render_upload_document()
    elif page == "Assistente AI":
        render_ai_assistant()
    elif page == "Scadenze e Calendario":
        render_deadlines()

# Esegui l'applicazione
if __name__ == "__main__":
    main()
