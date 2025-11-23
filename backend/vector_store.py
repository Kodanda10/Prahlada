import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import pickle

# --- FAISS Vector Store for Semantic Search ---

class VectorStore:
    """
    A wrapper for FAISS to handle document embedding and searching.
    This is designed as a singleton to avoid reloading the model and index.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VectorStore, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name='all-MiniLM-L6-v2', index_path='data/faiss_index.bin', metadata_path='data/faiss_metadata.pkl'):
        # Ensure __init__ is only run once
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        print("Initializing Vector Store...")
        self.model_name = model_name
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Ensure data directory exists
        try:
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            print(f"Data directory ensured: {os.path.dirname(index_path)}")
        except Exception as e:
            print(f"Warning: Could not create data directory: {e}")

        # Load the sentence transformer model
        print(f"Loading SentenceTransformer model: {model_name}...")
        try:
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

        texts = [doc['text'] for doc in documents]
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        
        if self.index is None:
            # Create a new index if one doesn't exist
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
            
        query_embedding = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1: # FAISS returns -1 for no result
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
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                print(f"Loading FAISS index from {self.index_path}...")
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"Index loaded successfully with {self.index.ntotal} vectors.")
            except Exception as e:
                print(f"Warning: Could not load existing index. Starting fresh. Error: {e}")
                self.index = None
                self.metadata = []
        else:
            print("No existing FAISS index found. A new one will be created on save.")

# Global instance to be used by the app
# Initialize lazily to avoid blocking during import
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance

# For backward compatibility, but initialization happens lazily
vector_store = None  # Will be initialized on first access via get_vector_store()
