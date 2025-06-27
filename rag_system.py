import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import requests
import json
from typing import List, Dict, Optional
import uuid
import os

class RAGSystem:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"): #using all-MiniLM-L6-v2 for embeddings
        """Initialize the RAG system with local models"""
        self.embedding_model_name = embedding_model_name #using all-MiniLM-L6-v2 for embeddings
        self.embedding_model = None #embedding model
        self.chroma_client = None #chroma client
        self.collection = None #collection  
        self.ollama_model = "llama2"  # Default model
        self.chunk_size = 500 #chunk size
        self.top_k = 3 #top k results   
        
        self._initialize_embedding_model()
        self._initialize_vector_db()
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model for embeddings"""
        try:
            print(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print("✅ Embedding model loaded successfully!")
        except Exception as e:
            raise Exception(f"Failed to load embedding model: {str(e)}")
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB for vector storage"""
        try:
            # Create persistent ChromaDB client
            persist_directory = "./chroma_db"
            os.makedirs(persist_directory, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="rag_documents",
                metadata={"description": "RAG system document collection"}
            )
            print("✅ Vector database initialized successfully!")
        except Exception as e:
            raise Exception(f"Failed to initialize vector database: {str(e)}")
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
            return []
        except:
            return []
    
    def set_model(self, model_name: str):
        """Set the Ollama model to use"""
        self.ollama_model = model_name
    
    def update_settings(self, chunk_size: int = None, top_k: int = None):
        """Update system settings"""
        if chunk_size:
            self.chunk_size = chunk_size
        if top_k:
            self.top_k = top_k
    
    def add_documents(self, document_chunks: List[Dict], source_filename: str):
        """Add document chunks to the vector database"""
        try:
            texts = []
            metadatas = []
            ids = []
            
            for chunk in document_chunks:
                chunk_id = str(uuid.uuid4())
                texts.append(chunk['content'])
                
                # Enhanced metadata
                metadata = chunk['metadata'].copy()
                metadata['source_filename'] = source_filename
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Generate embeddings
            print(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Added {len(texts)} chunks from {source_filename} to vector database")
            
        except Exception as e:
            raise Exception(f"Failed to add documents: {str(e)}")
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the document collection"""
        try:
            count = self.collection.count()
            return {"count": count}
        except:
            return {"count": 0}
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = None) -> List[Dict]:
        """Retrieve relevant document chunks for a query"""
        if top_k is None:
            top_k = self.top_k
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            relevant_chunks = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    relevant_chunks.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })
            
            return relevant_chunks
            
        except Exception as e:
            raise Exception(f"Failed to retrieve relevant chunks: {str(e)}")
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate response using Ollama with retrieved context"""
        try:
            # Prepare context from retrieved chunks
            context = "\n\n".join([
                f"Document: {chunk['metadata'].get('filename', 'Unknown')}\n{chunk['content']}"
                for chunk in context_chunks
            ])
            
            # Create prompt
            prompt = f"""Based on the following context from the uploaded documents, please answer the question. If the answer cannot be found in the provided context, please say so.

Context:
{context}

Question: {query}

Answer:"""
            
            # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Sorry, I could not generate a response.')
            else:
                return f"Error calling Ollama API: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Failed to connect to Ollama. Please ensure Ollama is running. Error: {str(e)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def ask_question(self, question: str) -> str:
        """Complete RAG pipeline: retrieve relevant chunks and generate answer"""
        try:
            # Check if we have any documents
            if self.collection.count() == 0:
                return "No documents have been uploaded yet. Please upload some documents first."
            
            # Retrieve relevant chunks
            relevant_chunks = self.retrieve_relevant_chunks(question, self.top_k)
            
            if not relevant_chunks:
                return "I couldn't find any relevant information in the uploaded documents to answer your question."
            
            # Generate response using the retrieved context
            response = self.generate_response(question, relevant_chunks)
            
            # Add source information
            sources = list(set([chunk['metadata'].get('filename', 'Unknown') 
                              for chunk in relevant_chunks]))
            source_info = f"\n\n📚 Sources: {', '.join(sources)}"
            
            return response + source_info
            
        except Exception as e:
            return f"Error processing your question: {str(e)}"
    
    def clear_database(self):
        """Clear all documents from the database"""
        try:
            self.chroma_client.delete_collection("rag_documents")
            self.collection = self.chroma_client.get_or_create_collection(
                name="rag_documents",
                metadata={"description": "RAG system document collection"}
            )
            print("✅ Database cleared successfully!")
        except Exception as e:
            raise Exception(f"Failed to clear database: {str(e)}") 