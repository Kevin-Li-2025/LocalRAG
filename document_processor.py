import os
from typing import List, Dict
import PyPDF2
import docx
import tiktoken

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def process_document(self, file_path: str, filename: str) -> List[Dict]:
        """Process a document and return chunks with metadata"""
        # Extract text based on file type
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension == '.pdf':
            text = self._extract_pdf_text(file_path)
        elif file_extension == '.docx':
            text = self._extract_docx_text(file_path)
        elif file_extension == '.txt':
            text = self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Clean and chunk the text
        cleaned_text = self._clean_text(text)
        chunks = self._chunk_text(cleaned_text)
        
        # Create document chunks with metadata
        document_chunks = []
        for i, chunk in enumerate(chunks):
            document_chunks.append({
                'content': chunk,
                'metadata': {
                    'filename': filename,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_type': file_extension[1:],  # Remove the dot
                    'chunk_size': len(chunk)
                }
            })
        
        return document_chunks
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove empty lines and normalize
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text into smaller pieces using token-based splitting"""
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))
            
            # If adding this sentence would exceed chunk size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                    current_chunk = overlap_text + " " + sentence
                    current_tokens = len(self.encoding.encode(current_chunk))
                else:
                    current_chunk = sentence
                    current_tokens = sentence_tokens
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting"""
        # Basic sentence splitting on periods, exclamation marks, and question marks
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get the last part of text for overlap"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= overlap_size:
            return text
        
        overlap_tokens = tokens[-overlap_size:]
        return self.encoding.decode(overlap_tokens)
    
    def update_chunk_size(self, chunk_size: int):
        """Update chunk size"""
        self.chunk_size = chunk_size 