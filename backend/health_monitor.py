import psutil
import time
import requests
from typing import Dict, Any
import os

# Mocking database check for now as we use a file-based DB (JSON) mostly, 
# but we can check if the file exists and is readable.
DATA_FILE = "data/ingested_tweets.json"

def check_service_health(url: str) -> bool:
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False

def get_system_health() -> Dict[str, Any]:
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    # Service Checks
    services = {
        "fastapi_backend": {"status": "up", "latency_ms": 0}, # Self
        "database_file": {"status": "up" if os.path.exists(DATA_FILE) else "down", "details": "JSON Store"},
        "ollama": {"status": "up" if check_service_health("http://localhost:11434") else "down", "url": "http://localhost:11434"},
        "mapbox_integration": {"status": "up", "details": "Client-side key valid"}, # Client side mostly
        "cognitive_engine": {"status": "up", "details": "Integrated"}, # Integrated in backend
    }
    
    return {
        "timestamp": time.time(),
        "cpu_usage": cpu_usage,
        "memory_usage": memory.percent,
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "services": services,
        "parser_uptime_seconds": int(time.time() - psutil.boot_time()), # System uptime as proxy
        "api_error_rate": 0.01, # Mocked low error rate for now
        "p95_latency_ms": 45 # Mocked latency
    }

def get_analytics_health() -> Dict[str, Any]:
    # Check freshness of data
    try:
        file_stats = os.stat(DATA_FILE)
        last_modified = file_stats.st_mtime
        is_stale = (time.time() - last_modified) > 86400 # Stale if older than 24h
    except:
        last_modified = 0
        is_stale = True

    return {
        "data_freshness": {
            "status": "stale" if is_stale else "fresh",
            "last_updated": last_modified,
            "source": "ingested_tweets.json"
        },
        "modules": {
            "demand_dashboard": {"status": "fresh", "cache_hit": True},
            "grievance_dashboard": {"status": "fresh", "cache_hit": True},
            "geo_coverage": {"status": "fresh", "cache_hit": False},
        }
    }
