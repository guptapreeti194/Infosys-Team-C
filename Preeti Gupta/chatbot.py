import streamlit as st
import requests
import json
import PyPDF2
import docx
from pathlib import Path
import re
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Document Intelligence System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-document-system',
        'Report a bug': "https://github.com/yourusername/ai-document-system/issues",
        'About': "# AI Document Intelligence System\nAdvanced document processing with AI-powered analysis."
    }
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Info boxes */
   /* Info boxes */
.info-box {
    background: #ffffff;
    border-left: 4px solid var(--primary-color);
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    color: #1e293b; /* Darker text for visibility */
}

.info-box strong {
    font-size: 1.05rem;
    color: var(--primary-color);
}

    
    /* Statistics panel */
    .stats-panel {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Document extraction functions
def extract_text_from_pdf(file):
    """Extract text from PDF file with error handling"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return None

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting DOCX: {str(e)}")
        return None

def extract_text_from_txt(file):
    """Extract text from TXT file"""
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error extracting TXT: {str(e)}")
        return None

def extract_document(file):
    """Extract text based on file type"""
    file_extension = Path(file.name).suffix.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file)
    elif file_extension == '.docx':
        return extract_text_from_docx(file)
    elif file_extension == '.txt':
        return extract_text_from_txt(file)
    else:
        st.error(f"Unsupported file type: {file_extension}")
        return None

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks with overlap"""
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)
        i += chunk_size - overlap
        if i >= len(words):
            break
    
    return chunks

def analyze_document(text):
    """Analyze document and extract statistics"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    paragraphs = text.split('\n\n')
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "paragraph_count": len([p for p in paragraphs if p.strip()]),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "unique_words": len(set(word.lower() for word in words))
    }

def create_document_json(filename, text, chunks, analysis):
    """Create comprehensive JSON structure for the document"""
    doc_json = {
        "filename": filename,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "full_text": text,
        "analysis": analysis,
        "metadata": {
            "total_characters": len(text),
            "total_words": len(text.split()),
            "total_chunks": len(chunks),
            "file_size": len(text.encode('utf-8'))
        },
        "chunks": [
            {
                "chunk_id": i,
                "text": chunk,
                "word_count": len(chunk.split()),
                "char_count": len(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]
    }
    return doc_json

def get_available_models():
    """Get list of available Ollama models"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        return []
    except Exception as e:
        return []

def query_ollama(prompt, model="llama3.2"):
    """Send query to Ollama API with streaming support"""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Error connecting to Ollama: {str(e)}"

def export_chat_history(chat_history):
    """Export chat history as JSON"""
    export_data = {
        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_messages": len(chat_history),
        "conversation": chat_history
    }
    return json.dumps(export_data, indent=2)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Document Intelligence System</h1>
    <p>Advanced Document Processing & Intelligent Conversational AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration Panel")
    
    # Model selection
    st.markdown("#### 🎯 AI Model Selection")
    available_models = get_available_models()
    
    if available_models:
        model_name = st.selectbox(
            "Select Model",
            available_models,
            help="Choose the AI model for processing"
        )
        st.markdown(f'<span class="status-badge status-success">✅ {len(available_models)} Models Available</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-warning">⚠️ Ollama Not Detected</span>', unsafe_allow_html=True)
        model_name = st.text_input("Model Name", "llama3.2")
        st.info("💡 Run: `ollama pull llama3.2`")
    
    st.markdown("---")
    
    # File upload
    st.markdown("#### 📁 Document Upload")
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt'],
        help="Supported: PDF, DOCX, TXT"
    )
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue())
        st.success(f"✅ {uploaded_file.name}")
        st.caption(f"📊 Size: {file_size / 1024:.2f} KB")
    
    st.markdown("---")
    
    # Chunking settings
    st.markdown("#### 🔧 Chunking Configuration")
    chunk_size = st.slider("Chunk Size (words)", 100, 2000, 500, 50)
    overlap = st.slider("Overlap (words)", 0, 300, 50, 10)
    
    st.markdown("---")
    
    # Advanced features
    st.markdown("#### 🚀 Advanced Features")
    
    col1, col2 = st.columns(2)
    with col1:
        show_stats = st.checkbox("📊 Statistics", value=True)
        show_json = st.checkbox("📄 JSON View", value=False)
    with col2:
        auto_summarize = st.checkbox("📝 Auto Summary", value=False)
        show_chunks = st.checkbox("🧩 Show Chunks", value=False)
    
    st.markdown("---")
    
    # Action buttons
    st.markdown("#### 🎮 Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset All", use_container_width=True):
            st.session_state.document_json = None
            st.session_state.chat_history = []
            st.rerun()
    
    if st.session_state.get('chat_history'):
        if st.button("💾 Export Chat", use_container_width=True):
            export_data = export_chat_history(st.session_state.chat_history)
            st.download_button(
                "⬇️ Download JSON",
                export_data,
                f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json",
                use_container_width=True
            )

# Initialize session state
if 'document_json' not in st.session_state:
    st.session_state.document_json = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processing_time' not in st.session_state:
    st.session_state.processing_time = 0

# Process uploaded file
if uploaded_file and st.session_state.document_json is None:
    start_time = time.time()
    
    with st.spinner("🔄 Processing document..."):
        progress_bar = st.progress(0)
        
        # Extract text
        progress_bar.progress(25)
        extracted_text = extract_document(uploaded_file)
        
        if extracted_text:
            # Analyze document
            progress_bar.progress(50)
            analysis = analyze_document(extracted_text)
            
            # Create chunks
            progress_bar.progress(75)
            chunks = chunk_text(extracted_text, chunk_size, overlap)
            
            # Create JSON structure
            doc_json = create_document_json(uploaded_file.name, extracted_text, chunks, analysis)
            st.session_state.document_json = doc_json
            st.session_state.processing_time = time.time() - start_time
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            
            st.success(f"✅ Document processed in {st.session_state.processing_time:.2f}s")
            st.balloons()

# Display document information
if st.session_state.document_json:
    doc = st.session_state.document_json
    
    # Metrics row
    st.markdown("### 📊 Document Analytics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📝 Total Words</div>
            <div class="metric-value">{doc['analysis']['word_count']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🧩 Chunks</div>
            <div class="metric-value">{doc['metadata']['total_chunks']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📄 Sentences</div>
            <div class="metric-value">{doc['analysis']['sentence_count']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔤 Unique Words</div>
            <div class="metric-value">{doc['analysis']['unique_words']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed statistics
    if show_stats:
        with st.expander("📈 Detailed Statistics", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Characters", f"{doc['analysis']['character_count']:,}")
                st.metric("Paragraphs", doc['analysis']['paragraph_count'])
                st.metric("File Size", f"{doc['metadata']['file_size'] / 1024:.2f} KB")
            with col2:
                st.metric("Avg Word Length", f"{doc['analysis']['avg_word_length']:.2f}")
                st.metric("Upload Time", doc['upload_time'])
                st.metric("Processing Time", f"{st.session_state.processing_time:.2f}s")
    
    # Show chunks
    if show_chunks:
        with st.expander("🧩 Document Chunks", expanded=False):
            for chunk in doc['chunks'][:5]:
                st.markdown(f"**Chunk {chunk['chunk_id']}** ({chunk['word_count']} words)")
                st.text_area("", chunk['text'], height=100, key=f"chunk_{chunk['chunk_id']}")
    
    # Show JSON
    if show_json:
        with st.expander("📄 JSON Structure", expanded=False):
            st.json(doc)
    
    # Auto-summarize
    if auto_summarize and len(st.session_state.chat_history) == 0:
        with st.spinner("🤖 Generating automatic summary..."):
            summary_prompt = f"""Analyze this document and provide a comprehensive summary:

Document: {doc['filename']}
Word Count: {doc['analysis']['word_count']}

Content Preview:
{doc['chunks'][0]['text'][:1000]}...

Provide:
1. Main topic/theme
2. Key points (3-5 bullet points)
3. Overall summary (2-3 sentences)"""
            
            summary = query_ollama(summary_prompt, model_name)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"📝 **Auto-Generated Summary**\n\n{summary}"
            })

# Main chat interface
st.markdown("---")
st.markdown("### 💬 Intelligent Chat Interface")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested prompts (if no chat history)
if len(st.session_state.chat_history) == 0:
    st.markdown("### 💡 Try These Interactions:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📚 Document Tasks**
        - "Summarize this document"
        - "What are the main points?"
        - "List all courses/items"
        - "Translate to Hindi"
        """)
    
    with col2:
        st.markdown("""
        **🤖 General Chat**
        - "Explain AI to me"
        - "Write me a poem"
        - "Tell me a joke"
        - "How does gravity work?"
        """)
    
    with col3:
        st.markdown("""
        **🎯 Creative Tasks**
        - "Write Python code"
        - "Generate ideas"
        - "Help with homework"
        - "Career advice"
        """)

# Chat input
user_question = st.chat_input("💭 Chat like ChatGPT/Claude - Ask ANYTHING: questions, coding, creative writing, analysis, translations...")

if user_question:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Prepare prompt
    if st.session_state.document_json:
        doc = st.session_state.document_json
        
        # Check if user is asking about specific chunk
        chunk_match = re.search(r'chunk\s*(\d+)', user_question.lower())
        
        if chunk_match:
            # User asking about specific chunk
            chunk_num = int(chunk_match.group(1))
            if chunk_num < len(doc['chunks']):
                doc_context = f"""
📄 **Document:** {doc['filename']}

**Full Content of Chunk {chunk_num}:**
{doc['chunks'][chunk_num]['text']}

**Chunk Statistics:**
- Word Count: {doc['chunks'][chunk_num]['word_count']}
- Character Count: {doc['chunks'][chunk_num]['char_count']}
"""
            else:
                doc_context = f"⚠️ Chunk {chunk_num} does not exist. Document has {len(doc['chunks'])} chunks (0-{len(doc['chunks'])-1})."
        else:
            # General document question - include all chunks
            doc_context = f"""
📄 **Document Context Available:**
- Filename: {doc['filename']}
- Total Words: {doc['analysis']['word_count']:,}
- Total Chunks: {doc['metadata']['total_chunks']}

**All Document Chunks (Full Content):**
"""
            for chunk in doc['chunks']:
                doc_context += f"\n\n{'='*50}\n**[Chunk {chunk['chunk_id']}]** ({chunk['word_count']} words)\n{'='*50}\n{chunk['text']}\n"
        
        prompt = f"""{doc_context}

**User Question:** {user_question}

**Instructions:**
- Provide complete, detailed information from the document
- List ALL items, courses, or options mentioned
- Use bullet points for clarity
- Include all relevant details (codes, names, requirements)
- If asking about a specific chunk, provide ALL content from that chunk
- Be thorough and comprehensive
- Don't truncate or summarize unless asked

**Answer:**"""
    else:
        prompt = f"""**User Question:** {user_question}

**Instructions:**
- Provide clear, comprehensive answers
- Support multiple languages
- Be helpful and informative

**Answer:**"""
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = query_ollama(prompt, model_name)
            st.markdown(response)
    
    # Add assistant response
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Footer with info
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
        <strong>🎯 ChatGPT/Claude Features</strong><br>
        • Natural conversations<br>
        • Code generation<br>
        • Creative writing<br>
        • Problem solving
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <strong>🚀 Advanced Capabilities</strong><br>
        • Document analysis<br>
        • Multi-language support<br>
        • Math & Science help<br>
        • Career guidance
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
        <strong>💡 Use Cases</strong><br>
        • Chat about anything<br>
        • Analyze documents<br>
        • Learn new topics<br>
        • Get creative help
    </div>
    """, unsafe_allow_html=True)

st.markdown("**🔗 Status:** Ollama running on `http://localhost:11434`")