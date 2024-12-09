import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

encoding_model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_chunking(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Split text into semantic chunks using LangChain's RecursiveCharacterTextSplitter"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    return text_splitter.split_text(text)

class CityVectorDB:
    def __init__(self):
        self.dimension = 384  # dimension of all-MiniLM-L6-v2 embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        self.cities_data = []
        self.chunks_metadata = []
    
    def add_city(self, city: str, description: str):
        # Create chunks
        chunks = semantic_chunking(description)
        
        # Create embeddings for chunks
        embeddings = encoding_model.encode(chunks)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            self.chunks_metadata.append({
                'city': city,
                'chunk': chunk,
                'chunk_id': len(self.chunks_metadata) + i
            })
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        # Create query embedding
        query_vector = encoding_model.encode([query])
        
        # Search in FAISS
        distances, indices = self.index.search(query_vector.astype('float32'), k)
        
        # Get results
        results = []
        for idx in indices[0]:
            if idx != -1:  # FAISS returns -1 if there aren't enough results
                results.append(self.chunks_metadata[idx])
        
        return results
    
    def save(self, filename: str):
        # Save FAISS index
        faiss.write_index(self.index, f"{filename}.index")
        # Save metadata
        with open(f"{filename}.metadata", 'wb') as f:
            pickle.dump(self.chunks_metadata, f)
    
    def load(self, filename: str):
        # Load FAISS index
        self.index = faiss.read_index(f"{filename}.index")
        # Load metadata
        with open(f"{filename}.metadata", 'rb') as f:
            self.chunks_metadata = pickle.load(f)