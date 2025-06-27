import streamlit as st
import os
import tempfile
from document_processor import DocumentProcessor
from rag_system import RAGSystem
import time

# Page configuration
st.set_page_config(
    page_title="Local RAG System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e1f5fe;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGSystem()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False

def main():
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📚 Local RAG System</h1>', unsafe_allow_html=True)
    st.markdown("**Upload your documents and ask questions using completely free local models!**")
    
    # Sidebar for document management
    with st.sidebar:
        st.header("📄 Document Management")
        
        # Ollama connection status
        with st.expander("🔗 Ollama Connection", expanded=True):
            if st.button("Check Ollama Status"):
                status = st.session_state.rag_system.check_ollama_status()
                if status:
                    st.success("✅ Ollama is running!")
                else:
                    st.error("❌ Ollama not detected. Please install and start Ollama.")
                    st.markdown("""
                    **To install Ollama:**
                    1. Visit [ollama.ai](https://ollama.ai)
                    2. Download and install
                    3. Run: `ollama pull llama2` or `ollama pull mistral`
                    """)
        
        # File upload section
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload PDF, DOCX, or TXT files"
        )
        
        if uploaded_files:
            if st.button("Process Documents", type="primary"):
                process_documents(uploaded_files)
        
        # Document statistics
        if st.session_state.documents_loaded:
            st.success("✅ Documents loaded successfully!")
            stats = st.session_state.rag_system.get_collection_stats()
            st.metric("Documents in database", stats.get('count', 0))
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Chat with your documents")
        
        # Chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        if st.session_state.documents_loaded:
            user_question = st.text_input("Ask a question about your documents:", key="user_input")
            
            col_send, col_clear = st.columns([1, 1])
            with col_send:
                if st.button("Send", type="primary") and user_question:
                    handle_question(user_question)
            
            with col_clear:
                if st.button("Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()
        else:
            st.info("👆 Please upload and process documents first to start chatting!")
    
    with col2:
        st.header("🔧 Settings")
        
        # Model selection
        available_models = st.session_state.rag_system.get_available_models()
        if available_models:
            selected_model = st.selectbox(
                "Select Ollama Model",
                available_models,
                help="Choose which local model to use for answering questions"
            )
            st.session_state.rag_system.set_model(selected_model)
        else:
            st.warning("No Ollama models found. Please pull a model first.")
        
        # Retrieval settings
        st.subheader("Retrieval Settings")
        chunk_size = st.slider("Chunk Size", 200, 1000, 500, help="Size of text chunks for retrieval")
        top_k = st.slider("Top K Results", 1, 10, 3, help="Number of relevant chunks to retrieve")
        
        st.session_state.rag_system.update_settings(chunk_size=chunk_size, top_k=top_k)

def process_documents(uploaded_files):
    """Process uploaded documents"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        processor = DocumentProcessor()
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Process document
                chunks = processor.process_document(tmp_file_path, uploaded_file.name)
                
                # Add to RAG system
                st.session_state.rag_system.add_documents(chunks, uploaded_file.name)
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
            
            progress_bar.progress((i + 1) / total_files)
        
        st.session_state.documents_loaded = True
        status_text.text("✅ All documents processed successfully!")
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")

def handle_question(question):
    """Handle user question and generate response"""
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # Generate response
    with st.spinner("Thinking..."):
        try:
            response = st.session_state.rag_system.ask_question(question)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

if __name__ == "__main__":
    main() 