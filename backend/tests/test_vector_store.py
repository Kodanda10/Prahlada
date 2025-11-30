"""
Unit tests for vector_store module.

Tests FAISS-based vector search functionality.
"""

import os
import pytest
from unittest.mock import MagicMock, patch, mock_open

# Set environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["AUTH_ALGORITHM"] = "HS256"
os.environ["AUTH_TOKEN_EXPIRE_MINUTES"] = "60"

from backend.vector_store import VectorStore


class TestVectorStore:
    """Unit tests for VectorStore class."""

    @pytest.fixture
    def mock_faiss(self):
        """Mock FAISS module."""
        with patch('backend.vector_store.faiss') as mock_faiss:
            # Mock FAISS index
            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.IndexIDMap.return_value = mock_index
            mock_faiss.read_index.return_value = mock_index
            mock_faiss.write_index.return_value = None

            yield mock_faiss

@pytest.fixture
def mock_sentence_transformer(self):
    """Mock SentenceTransformer."""
    with patch('backend.vector_store.SentenceTransformer') as mock_st:
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        # Return numpy array-like objects for proper astype() calls
        import numpy as np
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype='float32')
        mock_st.return_value = mock_model

        yield mock_st

    @pytest.fixture
    def vector_store(self, mock_faiss, mock_sentence_transformer):
        """VectorStore instance with mocked dependencies."""
        # Reset singleton instance for testing
        VectorStore._instance = None
        store = VectorStore()
        return store

    def test_init_creates_new_index(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should create new FAISS index on initialization."""
        # Verify FAISS index was created
        mock_faiss.IndexFlatL2.assert_called_once_with(384)  # Default dimension
        mock_faiss.IndexIDMap.assert_called_once()

        # Verify SentenceTransformer was initialized
        mock_sentence_transformer.assert_called_once_with('all-MiniLM-L6-v2')

    def test_add_documents_empty_list(self, vector_store):
        """Should handle empty document list gracefully."""
        documents = []
        vector_store.add_documents(documents)

        # Should not crash, just return early
        assert vector_store.metadata == []

    def test_add_documents_success(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should add documents successfully."""
        documents = [
            {"tweet_id": "1", "text": "Document 1"},
            {"tweet_id": "2", "text": "Document 2"}
        ]

        vector_store.add_documents(documents)

        # Verify encoding was called with text list
        mock_sentence_transformer.return_value.encode.assert_called_once_with(
            ["Document 1", "Document 2"]
        )

        # Verify vectors were added to index
        mock_faiss.IndexIDMap.return_value.add_with_ids.assert_called_once()

        # Verify metadata was stored
        assert len(vector_store.metadata) == 2
        assert vector_store.metadata[0]["tweet_id"] == "1"

    def test_search_empty_index(self, vector_store):
        """Should return empty results when index is empty."""
        results = vector_store.search("test query", k=5)

        assert results == []

    def test_search_success(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should search documents successfully."""
        # Setup index with data
        vector_store.index = mock_faiss.IndexIDMap.return_value
        vector_store.index.ntotal = 2
        vector_store.metadata = [
            {"tweet_id": "1", "text": "Document 1"},
            {"tweet_id": "2", "text": "Document 2"}
        ]

        # Mock search results
        mock_distances = [[0.1, 0.2]]
        mock_indices = [[0, 1]]
        vector_store.index.search.return_value = (mock_distances, mock_indices)

        results = vector_store.search("test query", k=2)

        # Verify query was encoded
        mock_sentence_transformer.return_value.encode.assert_called_once_with(["test query"])

        # Verify search was called
        vector_store.index.search.assert_called_once()

        # Verify results
        assert len(results) == 2
        assert results[0]["metadata"]["tweet_id"] == "1"
        assert results[0]["distance"] == 0.1
        assert results[1]["metadata"]["tweet_id"] == "2"
        assert results[1]["distance"] == 0.2

    def test_search_empty_query(self, vector_store, mock_sentence_transformer):
        """Should handle empty query gracefully."""
        result = vector_store.search("", k=5)

        assert result == []

        # Verify encode was not called for empty query
        mock_sentence_transformer.return_value.encode.assert_not_called()

    def test_search_success(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should search documents successfully."""
        # Setup mock search results
        mock_index = mock_faiss.IndexFlatIP.return_value
        mock_index.search.return_value = (
            [[0.9, 0.8]],  # distances
            [[0, 1]]       # indices
        )

        # Add some test metadata
        vector_store.metadata = [
            {"text": "Document 1", "id": "1"},
            {"text": "Document 2", "id": "2"}
        ]

        result = vector_store.search("test query", k=2)

        # Verify query was encoded
        mock_sentence_transformer.return_value.encode.assert_called_once_with(["test query"])

        # Verify search was called
        mock_index.search.assert_called_once()

        # Verify results
        assert len(result) == 1
        assert result[0]["text"] == "Document 1"
        assert result[0]["score"] == 0.9
        assert result[0]["metadata"]["id"] == "1"

    def test_search_no_metadata(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should handle search without metadata."""
        mock_index = mock_faiss.IndexFlatIP.return_value
        mock_index.search.return_value = ([[0.9]], [[0]])

        # No metadata stored
        vector_store.metadata = []

        result = vector_store.search("test query", k=1)

        assert len(result) == 1
        assert result[0]["text"] == ""  # Empty text when no metadata
        assert result[0]["score"] == 0.9
        assert result[0]["metadata"] == {}

    def test_search_with_k_parameter(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should respect k parameter in search."""
        mock_index = mock_faiss.IndexFlatIP.return_value
        mock_index.search.return_value = (
            [[0.9, 0.8, 0.7]],  # distances
            [[0, 1, 2]]         # indices
        )

        vector_store.metadata = [
            {"text": "Doc 1"}, {"text": "Doc 2"}, {"text": "Doc 3"}
        ]

        result = vector_store.search("test", k=2)

        assert len(result) == 2  # Should return only top 2
        assert result[0]["score"] == 0.9
        assert result[1]["score"] == 0.8

    def test_save_index_success(self, vector_store, mock_faiss):
        """Should save index successfully."""
        with patch('builtins.open', mock_open()) as mock_file:
            result = vector_store.save("test_path.bin")

            assert result is None
            mock_faiss.write_index.assert_called_once()

    def test_save_index_failure(self, vector_store, mock_faiss):
        """Should handle save failure gracefully."""
        mock_faiss.write_index.side_effect = Exception("Save failed")

        with patch('builtins.open', mock_open()):
            result = vector_store.save("test_path.bin")

            assert result is None  # Method doesn't return error, just handles it

    def test_load_index_success(self, mock_faiss, mock_sentence_transformer):
        """Should load index successfully."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                store = VectorStore.load("test_path.bin")

                assert isinstance(store, VectorStore)
                mock_faiss.read_index.assert_called_once_with("test_path.bin")

    def test_load_index_file_not_exists(self, mock_faiss, mock_sentence_transformer):
        """Should create new index when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            store = VectorStore.load("nonexistent.bin")

            assert isinstance(store, VectorStore)
            # Should create new index, not load
            mock_faiss.read_index.assert_not_called()
            mock_faiss.IndexFlatIP.assert_called_once()

    def test_load_index_failure(self, mock_faiss, mock_sentence_transformer):
        """Should handle load failure gracefully."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                mock_faiss.read_index.side_effect = Exception("Load failed")

                store = VectorStore.load("test_path.bin")

                assert isinstance(store, VectorStore)
                # Should fall back to creating new index

    def test_add_documents_encoding_error(self, vector_store, mock_sentence_transformer):
        """Should handle encoding errors gracefully."""
        mock_sentence_transformer.return_value.encode.side_effect = Exception("Encoding failed")

        documents = ["Document 1", "Document 2"]

        result = vector_store.add_documents(documents)

        assert result is None
        # Should not crash, just skip adding

    def test_search_index_error(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should handle index search errors gracefully."""
        mock_index = mock_faiss.IndexFlatIP.return_value
        mock_index.search.side_effect = Exception("Search failed")

        result = vector_store.search("test query", k=5)

        assert result == []  # Should return empty results on error

    def test_search_with_empty_index(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should handle search on empty index."""
        mock_index = mock_faiss.IndexFlatIP.return_value
        mock_index.ntotal = 0  # Empty index

        result = vector_store.search("test query", k=5)

        assert result == []  # Should return empty results

    def test_add_documents_large_batch(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should handle large batches of documents."""
        large_batch = [f"Document {i}" for i in range(1000)]

        # Mock large embeddings
        large_embeddings = [[0.1 * i] * 384 for i in range(1000)]
        mock_sentence_transformer.return_value.encode.return_value = large_embeddings

        result = vector_store.add_documents(large_batch)

        assert result is None
        # Verify large batch was handled
        assert len(mock_sentence_transformer.return_value.encode.call_args[0][0]) == 1000

    def test_save_index_success(self, vector_store, mock_faiss):
        """Should save index successfully."""
        with patch('builtins.open', mock_open()):
            vector_store.save()

            mock_faiss.write_index.assert_called_once()

    def test_save_no_index(self, vector_store, mock_faiss):
        """Should handle save when no index exists."""
        vector_store.index = None
        vector_store.save()

        # Should not call write_index when no index
        mock_faiss.write_index.assert_not_called()

    def test_load_index_success(self, vector_store, mock_faiss):
        """Should load index successfully."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                vector_store.load()

                mock_faiss.read_index.assert_called_once()

    def test_load_no_index_file(self, vector_store, mock_faiss):
        """Should handle missing index file gracefully."""
        with patch('os.path.exists', return_value=False):
            vector_store.load()

            # Should not try to read non-existent file
            mock_faiss.read_index.assert_not_called()

    def test_search_with_special_characters(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should handle queries with special characters."""
        # Setup index with data
        vector_store.index = mock_faiss.IndexIDMap.return_value
        vector_store.index.ntotal = 1
        vector_store.metadata = [{"text": "matching doc", "tweet_id": "1"}]

        mock_distances = [[0.9]]
        mock_indices = [[0]]
        vector_store.index.search.return_value = (mock_distances, mock_indices)

        special_query = "test query with @mentions #hashtags & symbols!"
        result = vector_store.search_similar(special_query, k=1)

        assert len(result) == 1
        assert result[0]["tweet_id"] == "1"

    def test_search_unicode_query(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should handle Unicode queries."""
        # Setup index with data
        vector_store.index = mock_faiss.IndexIDMap.return_value
        vector_store.index.ntotal = 1
        vector_store.metadata = [{"text": "government scheme delhi capital", "tweet_id": "2"}]

        mock_distances = [[0.9]]
        mock_indices = [[0]]
        vector_store.index.search.return_value = (mock_distances, mock_indices)

        unicode_query = "सरकारी योजना दिल्ली राजधानी"
        result = vector_store.search_similar(unicode_query, k=1)

        assert len(result) == 1
        assert result[0]["tweet_id"] == "2"

    def test_rebuild_index_success(self, vector_store, mock_faiss, mock_sentence_transformer):
        """Should rebuild index successfully."""
        vector_store.metadata = [
            {"text": "Document 1", "tweet_id": "1"},
            {"text": "Document 2", "tweet_id": "2"}
        ]

        vector_store.rebuild_index()

        # Verify index was rebuilt
        assert vector_store.index is not None
        mock_faiss.IndexIDMap.return_value.add_with_ids.assert_called_once()

    def test_rebuild_index_empty_metadata(self, vector_store):
        """Should handle rebuild with empty metadata."""
        vector_store.metadata = []

        vector_store.rebuild_index()

        assert vector_store.index is None

    def test_save_success(self, vector_store, mock_faiss):
        """Should save index successfully."""
        vector_store.index = mock_faiss.IndexIDMap.return_value

        vector_store.save()

        mock_faiss.write_index.assert_called_once()

    def test_save_no_index(self, vector_store, mock_faiss):
        """Should handle save when no index exists."""
        vector_store.index = None

        vector_store.save()

        mock_faiss.write_index.assert_not_called()

    def test_load_index_success(self, vector_store, mock_faiss):
        """Should load index successfully."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                vector_store.load()

                mock_faiss.read_index.assert_called_once()

    def test_load_no_index_file(self, vector_store, mock_faiss):
        """Should handle missing index file."""
        with patch('os.path.exists', return_value=False):
            vector_store.load()

            mock_faiss.read_index.assert_not_called()

    def test_index_tweets_invalid_structure(self, vector_store):
        """Should handle invalid tweet data structures."""
        invalid_tweets = [
            {"text": "Valid tweet"},
            {"invalid": "no text field"},
            "not a dict"
        ]

        # Should not crash, just log warnings
        vector_store.index_tweets(invalid_tweets)

    def test_search_similar_edge_cases(self, vector_store):
        """Test search_similar edge cases."""
        # Empty query
        result = vector_store.search_similar("")
        assert result == []

        # None query
        result = vector_store.search_similar(None)
        assert result == []

        # Whitespace query
        result = vector_store.search_similar("   ")
        assert result == []

    def test_index_tweets_embedding_failure(self, vector_store, mock_sentence_transformer):
        """Should handle embedding generation failure."""
        # Mock embedding failure
        mock_sentence_transformer.return_value.encode.side_effect = Exception("Embedding failed")

        tweets = [{"tweet_id": "1", "text": "Test tweet"}]

        with pytest.raises(ExternalServiceError) as exc_info:
            vector_store.index_tweets(tweets)

        assert "Indexing failed" in str(exc_info.value)
        assert exc_info.value.service == "vector_store"

    def test_index_tweets_index_creation_failure(self, vector_store, mock_faiss):
        """Should handle FAISS index creation failure."""
        # Mock index creation failure
        mock_faiss.IndexFlatL2.side_effect = Exception("Index creation failed")

        tweets = [{"tweet_id": "1", "text": "Test tweet"}]

        with pytest.raises(ExternalServiceError) as exc_info:
            vector_store.index_tweets(tweets)

        assert "Indexing failed" in str(exc_info.value)

    def test_search_similar_index_search_failure(self, vector_store, mock_faiss):
        """Should handle FAISS search failure."""
        # Setup index with data
        vector_store.index = mock_faiss.IndexIDMap.return_value
        vector_store.index.ntotal = 2
        vector_store.metadata = [
            {"tweet_id": "1", "text": "Document 1"},
            {"tweet_id": "2", "text": "Document 2"}
        ]

        # Mock search failure
        vector_store.index.search.side_effect = Exception("Search failed")

        with pytest.raises(ExternalServiceError) as exc_info:
            vector_store.search_similar("test query")

        assert "Search failed" in str(exc_info.value)
        assert exc_info.value.service == "vector_store"

    def test_rebuild_index_failure(self, vector_store, mock_sentence_transformer):
        """Should handle rebuild index failure."""
        vector_store.metadata = [{"tweet_id": "1", "text": "Document 1"}]

        # Mock embedding failure during rebuild
        mock_sentence_transformer.return_value.encode.side_effect = Exception("Embedding failed")

        with pytest.raises(ExternalServiceError) as exc_info:
            vector_store.rebuild_index()

        assert "Index rebuild failed" in str(exc_info.value)

    def test_save_failure(self, vector_store, mock_faiss):
        """Should handle save failure."""
        vector_store.index = mock_faiss.IndexIDMap.return_value
        vector_store.metadata = [{"tweet_id": "1", "text": "Document 1"}]

        # Mock write failure
        mock_faiss.write_index.side_effect = Exception("Write failed")

        with pytest.raises(ExternalServiceError) as exc_info:
            vector_store.save()

        assert "Save operation failed" in str(exc_info.value)