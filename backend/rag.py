import os
import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import re
import PyPDF2
from docx import Document

# Disable sentence_transformers to avoid slow import
SENTENCE_TRANSFORMERS_AVAILABLE = False
print("Using fast fallback embeddings (sentence-transformers disabled for speed)")

class EmbeddingService:
    def __init__(self):
        # Lazy load model
        self._model = None
        self.dimension = 384
    
    @property
    def model(self):
        if self._model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
            # Sentence transformers disabled for speed
            self._model = False
        return self._model
    
    def embed(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension
        
        # Use proper model if available
        if self.model and self.model is not False:
            return self.model.encode(text).tolist()
        
        # Fallback to simple hash-based embedding
        return self._simple_embed(text)
    
    def _simple_embed(self, text: str) -> List[float]:
        """Improved fallback embedding using word hashing with position weighting"""
        text = text.lower().strip()
        words = text.split()
        embedding = [0.0] * 384
        
        # Hash each word into the embedding space
        for i, word in enumerate(words[:50]):  # Limit to first 50 words
            # Use hash of word for more consistent embeddings
            word_hash = hash(word) % 384
            position_weight = 1.0 / (1.0 + i * 0.1)  # Reduce weight for later words
            
            # Spread each word across multiple dimensions
            for offset in range(5):
                idx = (word_hash + offset * 77) % 384
                embedding[idx] += position_weight
        
        # Normalize vector
        magnitude = np.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        try:
            import io
            reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        try:
            import io
            doc = Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    
    @staticmethod
    def process_file(filename: str, content: bytes) -> str:
        if filename.endswith('.pdf'):
            return DocumentProcessor.extract_text_from_pdf(content)
        elif filename.endswith('.docx'):
            return DocumentProcessor.extract_text_from_docx(content)
        elif filename.endswith(('.txt', '.md')):
            return DocumentProcessor.extract_text_from_txt(content)
        else:
            return f"Unsupported file type: {filename}"

class TextChunker:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        if not text:
            return []
        if len(text) < chunk_size:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(para) > chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) < chunk_size:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + " "
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

class VectorStore:
    def __init__(self):
        self.embeddings = EmbeddingService()
        self.documents = {}
        self.chunks = {}
        self.index = []
        self.vectors = None
    
    def add_document(self, doc_id: str, filename: str, text: str):
        self.documents[doc_id] = {
            'id': doc_id,
            'filename': filename,
            'text': text,
            'added_at': datetime.now(),
            'chunks': []
        }
        chunks = TextChunker.chunk_text(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            embedding = self.embeddings.embed(chunk)
            self.chunks[chunk_id] = {
                'id': chunk_id,
                'doc_id': doc_id,
                'content': chunk,
                'embedding': embedding,
                'filename': filename
            }
            self.index.append(chunk_id)
            self.documents[doc_id]['chunks'].append(chunk_id)
        self._rebuild_index()
    
    def _rebuild_index(self):
        if not self.index:
            self.vectors = None
            return
        embeddings = [self.chunks[cid]['embedding'] for cid in self.index]
        self.vectors = np.array(embeddings)
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict]:
        if not self.chunks or self.vectors is None:
            return []
        
        # Vector similarity search
        query_embedding = np.array(self.embeddings.embed(query))
        norm_q = np.linalg.norm(query_embedding)
        if norm_q == 0:
            return []
            
        norm_docs = np.linalg.norm(self.vectors, axis=1)
        dot_products = np.dot(self.vectors, query_embedding)
        similarities = dot_products / (norm_docs * norm_q)
        
        # Also do keyword matching as fallback
        query_words = set(query.lower().split())
        keyword_scores = []
        for chunk_id in self.index:
            chunk_text = self.chunks[chunk_id]['content'].lower()
            chunk_words = set(chunk_text.split())
            # Count matching words
            matches = len(query_words.intersection(chunk_words))
            keyword_scores.append(matches / max(len(query_words), 1))
        
        keyword_scores = np.array(keyword_scores)
        
        # Combine vector similarity and keyword matching
        combined_scores = similarities * 0.7 + keyword_scores * 0.3
        
        top_indices = np.argsort(combined_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = combined_scores[idx]
            if score >= threshold:
                chunk_id = self.index[idx]
                chunk = self.chunks[chunk_id]
                results.append({
                    'chunk_id': chunk_id,
                    'content': chunk['content'],
                    'similarity': float(score),
                    'filename': chunk['filename'],
                    'doc_id': chunk['doc_id']
                })
        return results
    
    def get_documents(self) -> List[Dict]:
        return list(self.documents.values())
    
    def clear(self):
        self.documents = {}
        self.chunks = {}
        self.index = []
        self.vectors = None

# Global instance
vector_store = VectorStore()
