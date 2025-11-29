"""
Lazy Import Utilities for Heavy ML Libraries

Defers loading of heavy dependencies (sentence_transformers, pymilvus, faiss)
until they are actually needed, preventing import-time blocking.
"""
import importlib
from typing import Any, Optional, Callable


class LazyModule:
    """
    Lazy loader for heavy modules.
    
    Only imports the module when an attribute is accessed.
    """
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._module = None
    
    def _load(self):
        """Load the module if not already loaded."""
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        """Lazy load module and return attribute."""
        module = self._load()
        return getattr(module, name)


class LazyClass:
    """
    Lazy loader for specific classes from heavy modules.
    
    Only imports and instantiates when called.
    """
    
    def __init__(self, module_name: str, class_name: str):
        self.module_name = module_name
        self.class_name = class_name
        self._class = None
    
    def _load(self):
        """Load the class if not already loaded."""
        if self._class is None:
            module = importlib.import_module(self.module_name)
            self._class = getattr(module, self.class_name)
        return self._class
    
    def __call__(self, *args, **kwargs) -> Any:
        """Instantiate the class with given arguments."""
        cls = self._load()
        return cls(*args, **kwargs)


class ConditionalImport:
    """
    Import that only loads if a condition is met.
    
    Useful for optional ML dependencies that can be disabled via env vars.
    """
    
    def __init__(self, module_name: str, condition_check: Optional[Callable[[], bool]] = None):
        self.module_name = module_name
        self.condition_check = condition_check or (lambda: True)
        self._module = None
        self._checked = False
    
    def _should_load(self) -> bool:
        """Check if module should be loaded."""
        if not self._checked:
            self._checked = True
            return self.condition_check()
        return self._module is not None
    
    def _load(self):
        """Load module if condition is met."""
        if self._module is None and self._should_load():
            try:
                self._module = importlib.import_module(self.module_name)
            except ImportError:
                self._module = None
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from module if loaded."""
        module = self._load()
        if module is None:
            raise ImportError(f"Module {self.module_name} not available or disabled")
        return getattr(module, name)
    
    def is_available(self) -> bool:
        """Check if module is available."""
        return self._load() is not None


# Environment-based conditional imports
import os

def _ml_enabled() -> bool:
    """Check if ML libraries should be loaded."""
    return os.getenv('PRAHLADA_NO_ML', '0') != '1'


# Pre-configured lazy imports for common heavy libraries
sentence_transformers = ConditionalImport('sentence_transformers', _ml_enabled)
pymilvus = ConditionalImport('pymilvus', _ml_enabled)
faiss = ConditionalImport('faiss', _ml_enabled)


# Convenience functions
def get_sentence_transformer(model_name: str = "intfloat/multilingual-e5-base"):
    """
    Get SentenceTransformer model with lazy loading.
    
    Args:
        model_name: Model identifier
        
    Returns:
        SentenceTransformer instance
        
    Raises:
        ImportError: If sentence_transformers not available or disabled
    """
    if not sentence_transformers.is_available():
        raise ImportError("sentence_transformers not available. Install with: pip install sentence-transformers")
    
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name)


def get_milvus_client(uri: str = "http://localhost:19530"):
    """
    Get MilvusClient with lazy loading.
    
    Args:
        uri: Milvus connection URI
        
    Returns:
        MilvusClient instance
        
    Raises:
        ImportError: If pymilvus not available or disabled
    """
    if not pymilvus.is_available():
        raise ImportError("pymilvus not available. Install with: pip install pymilvus")
    
    from pymilvus import MilvusClient
    return MilvusClient(uri=uri)


def get_faiss_index(dimension: int, index_type: str = "Flat"):
    """
    Get FAISS index with lazy loading.
    
    Args:
        dimension: Vector dimension
        index_type: Index type ('Flat', 'IVF', etc.)
        
    Returns:
        FAISS index instance
        
    Raises:
        ImportError: If faiss not available or disabled
    """
    if not faiss.is_available():
        raise ImportError("faiss not available. Install with: pip install faiss-cpu")
    
    import faiss as faiss_module
    
    if index_type == "Flat":
        return faiss_module.IndexFlatIP(dimension)
    elif index_type == "IVF":
        quantizer = faiss_module.IndexFlatIP(dimension)
        return faiss_module.IndexIVFFlat(quantizer, dimension, 100)
    else:
        raise ValueError(f"Unknown index type: {index_type}")


# Usage example:
if __name__ == "__main__":
    print("Testing lazy imports...")
    
    # Test 1: Check environment
    print(f"ML libraries enabled: {_ml_enabled()}")
    
    # Test 2: Module loads only when accessed
    print("✅ Lazy import utilities ready (no heavy libraries loaded yet)")
    
    # Uncomment to actually test loading:
    # if sentence_transformers.is_available():
    #     print("Loading SentenceTransformer...")
    #     model = get_sentence_transformer()
    #     print(f"✅ Model loaded: {model}")
