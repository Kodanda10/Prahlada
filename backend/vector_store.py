import numpy as np
import faiss
import os
import pickle
from typing import Optional, Any

# --- FAISS Vector Store for Semantic Search ---

class VectorStore:
    """
    A wrapper for FAISS to handle document embedding and searching.
    This is designed as a singleton to avoid reloading the model and index.
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2', index_path='data/faiss_index.bin', metadata_path='data/faiss_metadata.pkl'):
        # Ensure __init__ is only run once per instance
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        print(f"Initializing Vector Store at {index_path}...")
        self.model_name = model_name
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = None  # Lazy load
        self.dimension = None
        
        # Ensure data directory exists
        try:
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            print(f"Data directory ensured: {os.path.dirname(index_path)}")
        except Exception as e:
            print(f"Warning: Could not create data directory: {e}")

    def _ensure_model_loaded(self):
        """Lazy load the model"""
        if self.model is not None:
            return

        print(f"Loading SentenceTransformer model: {self.model_name}...")
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"Model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            import traceback
            print(f"ERROR: Failed to load SentenceTransformer model:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
        except Exception as e:
            import traceback
            print(f"ERROR: Failed to load SentenceTransformer model:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            raise  # Re-raise since model is required
        
        self.index = None
        self.metadata = [] # List of dictionaries, e.g., {'tweet_id': '...', 'text': '...'}

        print("Loading FAISS index (if exists)...")
        self.load()
        print("Vector Store initialized.")
        self.initialized = True

    def add_documents(self, documents: list[dict]):
        """
        Adds a list of documents to the index.
        Each document is a dict, e.g., {'tweet_id': '123', 'text': 'some content'}
        """
        if not documents:
            return

        self._ensure_model_loaded()
        texts = [doc['text'] for doc in documents]
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        
        if self.index is None:
            # Create a new index if one doesn't exist
            # Use IndexIDMap to support add_with_ids
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIDMap(self.index)
        
        # Generate new IDs starting from the current size of the metadata
        start_id = len(self.metadata)
        ids = np.arange(start_id, start_id + len(documents))

        self.index.add_with_ids(embeddings.astype('float32'), ids)
        self.metadata.extend(documents)
        print(f"Added {len(documents)} documents to FAISS index. Total size: {self.index.ntotal}")

    def search(self, query: str, k: int = 5):
        """
        Searches the index for the top k most similar documents.
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        self._ensure_model_loaded()
        try:
            query_embedding = self.model.encode([query]).astype('float32')
        except Exception as e:
            print(f"Vector search skipped: failed to encode query ({e})")
            return []

        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1: # FAISS returns -1 for no result
                if idx >= len(self.metadata):
                    # Metadata may be missing if index was saved without it; skip inconsistent rows
                    continue
                results.append({
                    "metadata": self.metadata[idx],
                    "distance": float(distances[0][i])
                })
        return results

    def save(self):
        """
        Saves the index and metadata to disk.
        """
        if self.index:
            print(f"Saving FAISS index to {self.index_path}...")
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            print("Save complete.")

    def load(self):
        """
        Loads the index and metadata from disk if they exist.
        """
        if os.path.exists(self.index_path):
            try:
                print(f"Loading FAISS index from {self.index_path}...")
                self.index = faiss.read_index(self.index_path)
                
                # Load metadata if it exists, otherwise start with empty list
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, 'rb') as f:
                        self.metadata = pickle.load(f)
                    print(f"Index loaded successfully with {self.index.ntotal} vectors and {len(self.metadata)} metadata entries.")
                else:
                    print(f"Index loaded with {self.index.ntotal} vectors. No metadata file found - starting with empty metadata.")
                    self.metadata = []
            except Exception as e:
                print(f"Warning: Could not load existing index. Starting fresh. Error: {e}")
                self.index = None
                self.metadata = []
        else:
            print("No existing FAISS index found. A new one will be created on save.")

# Global instances map
_vector_store_instances = {}

def get_vector_store(index_path: str = None) -> VectorStore:
    """Get or create a vector store instance for the given path."""
    global _vector_store_instances
    
    # Default path from env if not provided
    if index_path is None:
        index_path = os.getenv('FAISS_INDEX_PATH', 'data/faiss_index.bin')
        
    if index_path not in _vector_store_instances:
        # Derive metadata path from index path
        metadata_path = index_path.replace('.bin', '_metadata.pkl')
        model_name = os.getenv('FAISS_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        _vector_store_instances[index_path] = VectorStore(
            model_name=model_name,
            index_path=index_path,
            metadata_path=metadata_path
        )
    return _vector_store_instances[index_path]

# For backward compatibility, but initialization happens lazily
vector_store = None  # Will be initialized on first access via get_vector_store()
