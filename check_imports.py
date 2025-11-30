
print("Checking imports...")
try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence_transformers imported")
except ImportError as e:
    print(f"❌ sentence_transformers failed: {e}")

try:
    import faiss
    print("✅ faiss imported")
except ImportError as e:
    print(f"❌ faiss failed: {e}")

try:
    from pymilvus import MilvusClient
    print("✅ pymilvus imported")
except ImportError as e:
    print(f"❌ pymilvus failed: {e}")
