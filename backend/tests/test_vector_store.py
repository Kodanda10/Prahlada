"""
Tests for vector store (FAISS-based semantic search).
Mocks sentence transformers and FAISS to test logic without dependencies.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from backend.vector_store import VectorStore, get_vector_store


class TestVectorStore:
    """Test FAISS vector store operations."""
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    def test_vector_store_initialization(self, mock_faiss, mock_transformer):
        """Vector store should initialize correctly."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        # Reset singleton for testing
        VectorStore._instance = None
        store = VectorStore()
        
        assert store.dimension == 384
        assert store.model is not None
        assert store.index is None  # No index initially
        assert store.metadata == []
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    def test_add_documents(self, mock_faiss, mock_transformer):
        """Should add documents to index."""
        # Setup mocks
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embeddings = np.random.rand(2, 384).astype('float32')
        mock_model.encode.return_value = mock_embeddings
        mock_transformer.return_value = mock_model
        
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_id_map = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.IndexIDMap.return_value = mock_id_map
        
        # Reset singleton
        VectorStore._instance = None
        store = VectorStore()
        
        documents = [
            {'tweet_id': '123', 'text': 'First tweet'},
            {'tweet_id': '456', 'text': 'Second tweet'},
        ]
        
        store.add_documents(documents)
        
        assert len(store.metadata) == 2
        assert store.metadata[0]['tweet_id'] == '123'
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    def test_add_empty_documents(self, mock_faiss, mock_transformer):
        """Should handle empty document list."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        VectorStore._instance = None
        store = VectorStore()
        
        store.add_documents([])
        
        assert store.metadata == []
        assert store.index is None
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    def test_search(self, mock_faiss, mock_transformer):
        """Should search and return relevant documents."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_query_embedding = np.random.rand(1, 384).astype('float32')
        mock_model.encode.return_value = mock_query_embedding
        mock_transformer.return_value = mock_model
        
        mock_index = Mock()
        mock_index.ntotal = 2
        # Simulate search results: distances and indices
        mock_index.search.return_value = (
            np.array([[0.1, 0.5]]),  # distances
            np.array([[0, 1]])        # indices
        )
        
        VectorStore._instance = None
        store = VectorStore()
        store.index = mock_index
        store.metadata = [
            {'tweet_id': '123', 'text': 'First'},
            {'tweet_id': '456', 'text': 'Second'},
        ]
        
        results = store.search("test query", k=2)
        
        assert len(results) == 2
        assert results[0]['metadata']['tweet_id'] == '123'
        assert 'distance' in results[0]
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    def test_search_empty_index(self, mock_faiss, mock_transformer):
        """Should return empty results for empty index."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        VectorStore._instance = None
        store = VectorStore()
        store.index = None
        
        results = store.search("test query")
        
        assert results == []
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    @patch('os.path.exists')
    def test_save_index(self, mock_exists, mock_faiss, mock_transformer):
        """Should save index and metadata to disk."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        mock_index = Mock()
        
        VectorStore._instance = None
        store = VectorStore()
        store.index = mock_index
        store.metadata = [{'tweet_id': '123'}]
        
        with patch('builtins.open', create=True) as mock_open:
            store.save()
        
        mock_faiss.write_index.assert_called_once()
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    @patch('os.path.exists')
    def test_load_existing_index(self, mock_exists, mock_faiss, mock_transformer):
        """Should load existing index from disk."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        mock_exists.return_value = True
        mock_index = Mock()
        mock_index.ntotal = 5
        mock_faiss.read_index.return_value = mock_index
        
        VectorStore._instance = None
        
        with patch('builtins.open', create=True), \
             patch('pickle.load', return_value=[{'tweet_id': '1'}]):
            store = VectorStore()
        
        assert store.index is not None
        assert len(store.metadata) > 0
    
    @patch('backend.vector_store.SentenceTransformer')
    @patch('backend.vector_store.faiss')
    def test_singleton_pattern(self, mock_faiss, mock_transformer):
        """Vector store should implement singleton pattern."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        VectorStore._instance = None
        store1 = VectorStore()
        store2 = VectorStore()
        
        assert store1 is store2
    
    @patch('backend.vector_store.VectorStore')
    def test_get_vector_store(self, mock_vector_store_class):
        """get_vector_store should return global instance."""
        import backend.vector_store as vs
        vs._vector_store_instance = None
        
        mock_instance = Mock()
        mock_vector_store_class.return_value = mock_instance
        
        result = get_vector_store()
        
        assert result is not None
