import streamlit as st

st.set_page_config(page_title="Email RAG Chatbot", layout="wide")

st.title("📧 Email RAG Chatbot")
st.write("Cerca email Gmail usando il linguaggio naturale.")

# Input utente
query = st.text_input("Scrivi la tua richiesta:", "")

if query:
    st.write(f"🔍 Cerco email per: '{query}'")
    # Qui integreremo: retrieval + generazione
    st.info("⚙️ Funzionalità in sviluppo...")