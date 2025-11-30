
try:
    from sentence_transformers import SentenceTransformer
    print("sentence_transformers is available")
except ImportError:
    print("sentence_transformers is NOT available")
