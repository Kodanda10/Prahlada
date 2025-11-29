"""
Cognitive module for Project Prahlada.

Provides AI/ML capabilities for tweet analysis and enhancement.
All cognitive operations are advisory and require human review.
"""

# Use lazy imports to avoid circular dependency issues
# Import functions will load modules on-demand

def get_cognitive_interface():
    """Lazy import of CognitiveInterface."""
    from .interface import get_cognitive_interface as _get
    return _get()

def configure_cognitive_interface(*args, **kwargs):
    """Lazy import of configure_cognitive_interface."""
    from .interface import configure_cognitive_interface as _config
    return _config(*args, **kwargs)

def get_phi_adapter():
    """Lazy import of PhiAdapter."""
    from .phi_adapter import get_phi_adapter as _get
    return _get()

def set_phi_adapter_config(*args, **kwargs):
    """Lazy import of set_phi_adapter_config."""
    from .phi_adapter import set_phi_adapter_config as _set
    return _set(*args, **kwargs)

# Only expose factory functions, not classes
# This prevents eager loading of modules
__all__ = [
    # Main interfaces (lazy loaded)
    "get_cognitive_interface",
    "configure_cognitive_interface",
    
    # Phi 3.5 components (lazy loaded)
    "get_phi_adapter",
    "set_phi_adapter_config",
]

# Legacy support: Allow direct class imports for backward compatibility
# These will trigger module loading only when accessed
def __getattr__(name):
    """Lazy attribute access for backward compatibility."""
    if name == "CognitiveInterface":
        from .interface import CognitiveInterface
        return CognitiveInterface
    elif name == "PhiAdapter":
        from .phi_adapter import PhiAdapter
        return PhiAdapter
    elif name == "PhiSuggestions":
        from .phi_adapter import PhiSuggestions
        return PhiSuggestions
    elif name == "OllamaClient":
        from .ollama_client import OllamaClient
        return OllamaClient
    elif name == "CognitiveEngine":
        from .engine import CognitiveEngine
        return CognitiveEngine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")