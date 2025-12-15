# simple_chat.py - EMERGENCY DIRECT RAG CHATBOT (FIXED UI)

import streamlit as st
import os
import tempfile
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import ollama

# --- CONFIGURATION ---
MODEL_NAME = "llama3:latest"
EMBEDDING_MODEL = "nomic-embed-text" # Falls back if not found

# Initialize ChromaDB (Vector Store)
DB_PATH = "./chroma_db_data"
client = chromadb.PersistentClient(path=DB_PATH)

# --------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------

def get_ollama_embedding(text):
    """Generate embedding using Ollama."""
    try:
        response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
        return response["embedding"]
    except:
        response = ollama.embeddings(model=MODEL_NAME, prompt=text)
        return response["embedding"]

def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def process_and_store_document(uploaded_file):
    text = extract_text_from_pdf(uploaded_file)
    chunks = chunk_text(text)
    
    try:
        client.delete_collection(name="rag_demo")
    except:
        pass
    collection = client.create_collection(name="rag_demo")
    
    ids = [str(i) for i in range(len(chunks))]
    embeddings = []
    
    # Simple progress bar
    progress_bar = st.progress(0)
    for i, chunk in enumerate(chunks):
        emb = get_ollama_embedding(chunk)
        embeddings.append(emb)
        progress_bar.progress((i + 1) / len(chunks))
    progress_bar.empty() # Remove bar after done
        
    collection.add(documents=chunks, embeddings=embeddings, ids=ids)
    return collection

def query_rag(collection, question):
    question_embedding = get_ollama_embedding(question)
    results = collection.query(query_embeddings=[question_embedding], n_results=3)
    context_text = "\n\n".join(results['documents'][0])
    
    prompt = f"""
    You are a helpful assistant. Answer the question based ONLY on the following context.
    If the answer is not in the context, say you don't know.

    Context:
    {context_text}

    Question: 
    {question}
    """
    response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

# --------------------------------------------------------
# MAIN UI
# --------------------------------------------------------

st.set_page_config(page_title="Chatbot")
st.title("ClauseEase AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Processing Logic
collection = None
if uploaded_file:
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("Processing PDF... (This runs once)"):
            collection = process_and_store_document(uploaded_file)
            st.session_state.current_file = uploaded_file.name
            st.success("PDF Processed! Ready to chat.")
    
    # Get the collection reference
    try:
        collection = client.get_collection(name="rag_demo")
    except:
        pass

# Chat UI - Always show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT BAR IS NOW OUTSIDE THE IF BLOCK
if prompt := st.chat_input("Ask about the PDF..."):
    if not uploaded_file:
        st.error("⚠️ Please upload a PDF first to ask questions!")
    elif collection:
        # Show User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = query_rag(collection, prompt)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})