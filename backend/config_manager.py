import json
import os
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path("data/ui_config.json")

DEFAULT_CONFIG = {
    "titles": {
        "app_title": "Project Prahlada",
        "app_subtitle": "Social Media Analytics Dashboard",
        "home_tab": "होम (Home)",
        "review_tab": "समीक्षा (Review)",
        "analytics_tab": "एनालिटिक्स (Analytics)",
        "control_hub_tab": "कंट्रोल हब (Control Hub)"
    },
    "modules": {
        "controlhub_header_systemhealth": True,
        "controlhub_grid_analytics_sync": True,
        "controlhub_panel_mindmap_mapbox": True,
        "controlhub_panel_api_health": True,
        "controlhub_panel_title_editor": True,
        "analytics_chart_event_type": True,
        "analytics_map_visual": True,
        "analytics_chart_tour": True,
        "analytics_chart_development": True,
        "analytics_panel_community": True,
        "analytics_chart_schemes": True,
        "analytics_panel_target_groups": True,
        "analytics_panel_thematic": True,
        "analytics_panel_raigarh": True
    }
}

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def update_config(section: str, key: str, value: Any) -> Dict[str, Any]:
    config = load_config()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    save_config(config)
    return config
