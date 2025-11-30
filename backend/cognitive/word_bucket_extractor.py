"""
Semantic Word Bucket Extractor for Project Prahlada.

Extracts high-signal, semantic word buckets from tweets using:
1. Text Normalization (Hindi Nukta removal, Transliteration)
2. Entity Recognition (NER)
3. Semantic Embedding & Clustering (SentenceTransformers + FAISS)
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import logging

# Lazy loading for ML libraries
ML_AVAILABLE = True # Assume available, will check on load
SentenceTransformer = None
faiss = None

logger = logging.getLogger(__name__)

class TextNormalizer:
    """Handles Hindi text normalization and transliteration."""
    
    def __init__(self):
        self.nukta_map = {
            '\u0958': '\u0915', # क़ -> क
            '\u0959': '\u0916', # ख़ -> ख
            '\u095A': '\u0917', # ग़ -> ग
            '\u095B': '\u091C', # ज़ -> ज
            '\u095C': '\u0921', # ड़ -> ड
            '\u095D': '\u0922', # ढ़ -> ढ
            '\u095E': '\u092B', # फ़ -> फ
            '\u095F': '\u092F', # य़ -> य
        }

    def normalize(self, text: str) -> str:
        """
        Normalize Hindi text:
        1. Unicode normalization (NFC)
        2. Remove Nuktas
        3. Strip whitespace
        """
        if not text:
            return ""
            
        # 1. Unicode NFC
        text = unicodedata.normalize('NFC', text)
        
        # 2. Remove Nuktas
        for nukta_char, base_char in self.nukta_map.items():
            text = text.replace(nukta_char, base_char)
            
        # Also remove combining nukta char if present separately
        text = text.replace('\u093C', '') 
        
        return text.strip()

    def transliterate(self, text: str) -> str:
        """
        Simple rule-based transliteration (Placeholder).
        In production, use a library like `indic-transliteration`.
        For now, returns None to indicate not implemented fully.
        """
        return None  # TODO: Implement robust transliteration


class WordBucketExtractor:
    """
    Extracts and manages semantic word buckets.
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2", use_faiss: bool = True):
        self.normalizer = TextNormalizer()
        self.use_faiss = use_faiss
        self.model_name = model_name
        self.model = None
        self.index = None
        self.buckets_cache = {} # id -> {term, embedding, cluster_id}
        self.dimension = 384 # MiniLM dimension

    def _ensure_ml_loaded(self):
        """Lazy load ML components"""
        if not self.use_faiss or self.model is not None:
            return

        global SentenceTransformer, faiss, ML_AVAILABLE
        
        if SentenceTransformer is None:
            try:
                from sentence_transformers import SentenceTransformer as ST
                import faiss as F
                SentenceTransformer = ST
                faiss = F
                ML_AVAILABLE = True
            except ImportError:
                logger.error("ML libraries not found. Disabling semantic features.")
                ML_AVAILABLE = False
                self.use_faiss = False
                return

        try:
            logger.info(f"Loading SentenceTransformer: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.index = faiss.IndexFlatIP(self.dimension)
            logger.info("WordBucketExtractor initialized with FAISS")
        except Exception as e:
            logger.error(f"Failed to initialize ML components: {e}")
            self.use_faiss = False

    def extract_candidates(self, text: str) -> List[str]:
        """
        Extract candidate words/phrases from text.
        Simple logic: Split by space, remove stop words.
        TODO: Add N-gram extraction.
        """
        # Basic stop words (Hindi)
        stop_words = {
            "है", "हूँ", "हो", "था", "थी", "थे", "का", "की", "के", "में", "से", "को", "ने", 
            "पर", "और", "या", "तो", "भी", "ही", "कि", "जो", "कर", "रहे", "लिए", "वाला", "वाले"
        }
        
        # Clean and split
        words = re.findall(r'[\u0900-\u097F\w]+', text)
        candidates = []
        
        for w in words:
            if len(w) > 2 and w not in stop_words:
                candidates.append(w)
                
        return list(set(candidates)) # Unique

    def process_tweet(self, tweet_id: str, text: str, parsed_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a tweet to extract and cluster word buckets.
        """
        # Ensure ML is loaded
        self._ensure_ml_loaded()

        # 1. Extract Candidates
        candidates = self.extract_candidates(text)
        
        # 2. Add Parsed Entities (High Signal)
        if parsed_metadata.get('location'):
            loc = parsed_metadata['location']
            if isinstance(loc, dict):
                candidates.append(loc.get('canonical', ''))
            elif isinstance(loc, str):
                candidates.append(loc)
                
        if parsed_metadata.get('event_type'):
            candidates.append(parsed_metadata['event_type'])
            
        # Remove empty
        candidates = [c for c in candidates if c]
        
        buckets = []
        
        for term in candidates:
            norm_term = self.normalizer.normalize(term)
            
            bucket_entry = {
                "word": term,
                "normalized": norm_term,
                "type": "auto", # Default
                "cluster_id": None
            }
            
            # 3. Vectorize & Cluster (if ML available)
            if self.use_faiss and self.model:
                embedding = self.model.encode([norm_term])[0]
                # Normalize for Cosine Similarity
                faiss.normalize_L2(np.array([embedding]))
                
                # Search in Index
                if self.index.ntotal > 0:
                    D, I = self.index.search(np.array([embedding]), 1)
                    if D[0][0] > 0.85: # Threshold
                        # Found existing cluster
                        bucket_entry['cluster_id'] = f"cluster_{I[0][0]}" # Placeholder ID
                        bucket_entry['type'] = "existing_cluster"
                    else:
                        # New Cluster
                        self.index.add(np.array([embedding]))
                        bucket_entry['cluster_id'] = f"cluster_{self.index.ntotal - 1}"
                        bucket_entry['type'] = "new_cluster"
                else:
                    # First entry
                    self.index.add(np.array([embedding]))
                    bucket_entry['cluster_id'] = "cluster_0"
                    bucket_entry['type'] = "new_cluster"
            
            buckets.append(bucket_entry)
            
        return buckets

# Global Instance
_extractor = None

def get_word_bucket_extractor():
    global _extractor
    if _extractor is None:
        _extractor = WordBucketExtractor()
    return _extractor
