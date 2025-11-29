"""
Word Bucket FAISS Manager

Manages FAISS index for semantic word bucket clustering and deduplication.
Enables finding similar terms to avoid duplicate word buckets.
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WordBucketFAISS:
    """
    FAISS index manager for word bucket semantic search.
    
    Uses Inner Product similarity (cosine similarity with normalized vectors)
    to find semantically similar terms for clustering and deduplication.
    """
    
    def __init__(self, index_path: str = "data/word_buckets_faiss.bin", dimension: int = 768):
        """
        Initialize Word Bucket FAISS index.
        
        Args:
            index_path: Path to save/load FAISS index
            dimension: Embedding dimension (768 for multilingual-e5-base)
        """
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index = None
        self.metadata = []  # List of {bucket_id, term, type}
        
        # Ensure directory exists
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create index
        if self.index_path.exists():
            self.load()
        else:
            self._create_index()
    
    def _create_index(self):
        """Create new FAISS index"""
        # IndexFlatIP: Inner Product (cosine similarity with normalized vectors)
        # Fast and exact search, suitable for moderate-sized word bucket collections
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        logger.info(f"Created new FAISS index (dimension={self.dimension})")
    
    def add_bucket(
        self,
        bucket_id: int,
        term: str,
        embedding: np.ndarray,
        bucket_type: Optional[str] = None
    ):
        """
        Add a word bucket to the index.
        
        Args:
            bucket_id: Database ID of the word bucket
            term: The term/phrase
            embedding: 768-dim embedding vector
            bucket_type: Type of bucket (scheme, location, person, etc.)
        """
        if self.index is None:
            self._create_index()
        
        # Normalize embedding for cosine similarity
        embedding = embedding.astype('float32')
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Normalize to unit length for cosine similarity
        faiss.normalize_L2(embedding)
        
        # Add to index
        self.index.add(embedding)
        
        # Store metadata
        self.metadata.append({
            'bucket_id': bucket_id,
            'term': term,
            'type': bucket_type
        })
        
        logger.debug(f"Added word bucket: {term} (ID: {bucket_id}, Type: {bucket_type})")
    
    def add_buckets_batch(self, buckets: List[Dict]):
        """
        Add multiple word buckets at once.
        
        Args:
            buckets: List of dicts with keys: bucket_id, term, embedding, type
        """
        if not buckets:
            return
        
        embeddings = np.vstack([b['embedding'] for b in buckets]).astype('float32')
        faiss.normalize_L2(embeddings)
        
        self.index.add(embeddings)
        
        for bucket in buckets:
            self.metadata.append({
                'bucket_id': bucket['bucket_id'],
                'term': bucket['term'],
                'type': bucket.get('type')
            })
        
        logger.info(f"Added {len(buckets)} word buckets to index")
    
    def search_similar(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        Find similar word buckets.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of dicts with keys: bucket_id, term, type, similarity
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Normalize query
        query = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query)
        
        # Search
        distances, indices = self.index.search(query, min(k, self.index.ntotal))
        
        # Filter by similarity threshold and format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if dist >= min_similarity:  # Inner product similarity (higher is better)
                meta = self.metadata[idx]
                results.append({
                    'bucket_id': meta['bucket_id'],
                    'term': meta['term'],
                    'type': meta['type'],
                    'similarity': float(dist)
                })
        
        return results
    
    def find_duplicates(
        self,
        term: str,
        embedding: np.ndarray,
        similarity_threshold: float = 0.85
    ) -> List[Dict]:
        """
        Find potential duplicate word buckets.
        
        Args:
            term: Term to check
            embedding: Embedding of the term
            similarity_threshold: Threshold for considering duplicates
        
        Returns:
            List of similar buckets (likely duplicates)
        """
        similar = self.search_similar(
            embedding,
            k=10,
            min_similarity=similarity_threshold
        )
        
        # Filter out exact matches (same term)
        duplicates = [s for s in similar if s['term'].lower() != term.lower()]
        
        return duplicates
    
    def save(self):
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            logger.warning("No index to save")
            return
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        metadata_path = self.index_path.with_suffix('.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        logger.info(f"Saved Word Bucket FAISS index: {self.index_path} ({self.index.ntotal} buckets)")
    
    def load(self):
        """Load FAISS index and metadata from disk"""
        if not self.index_path.exists():
            logger.warning(f"Index file not found: {self.index_path}")
            self._create_index()
            return
        
        # Load FAISS index
        self.index = faiss.read_index(str(self.index_path))
        
        # Load metadata
        metadata_path = self.index_path.with_suffix('.pkl')
        if metadata_path.exists():
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            logger.warning("Metadata file not found, creating empty metadata")
            self.metadata = []
        
        logger.info(f"Loaded Word Bucket FAISS index: {self.index_path} ({self.index.ntotal} buckets)")
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        if self.index is None:
            return {'total_buckets': 0}
        
        type_counts = {}
        for meta in self.metadata:
            bucket_type = meta.get('type', 'unknown')
            type_counts[bucket_type] = type_counts.get(bucket_type, 0) + 1
        
        return {
            'total_buckets': self.index.ntotal,
            'dimension': self.dimension,
            'type_distribution': type_counts
        }


# Singleton instance
_word_bucket_faiss = None


def get_word_bucket_faiss(index_path: str = "data/word_buckets_faiss.bin") -> WordBucketFAISS:
    """Get or create Word Bucket FAISS instance"""
    global _word_bucket_faiss
    if _word_bucket_faiss is None:
        _word_bucket_faiss = WordBucketFAISS(index_path=index_path)
    return _word_bucket_faiss
