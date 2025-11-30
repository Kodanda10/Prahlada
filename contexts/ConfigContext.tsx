import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface UIConfig {
  titles: {
    app_title: string;
    app_subtitle: string;
    home_tab: string;
    review_tab: string;
    analytics_tab: string;
    control_hub_tab: string;
    [key: string]: string;
  };
  modules: {
    // Home
    home_header?: boolean;
    home_filters?: boolean;
    home_table?: boolean;

    // Review
    review_header?: boolean;
    review_queue?: boolean;
    review_ai_assistant?: boolean;
    review_semantic_search?: boolean;
    review_metrics?: boolean;

    // Analytics
    analytics_header?: boolean;
    analytics_summary?: boolean;
    analytics_geo?: boolean;
    analytics_tour?: boolean;
    analytics_development?: boolean;
    analytics_outreach?: boolean;
    analytics_schemes?: boolean;
    analytics_target_groups?: boolean;
    analytics_thematic?: boolean;
    analytics_raigarh?: boolean;

    // Control Hub
    controlhub_header_systemhealth?: boolean;
    controlhub_grid_analytics_sync?: boolean;
    controlhub_panel_title_editor?: boolean;
    controlhub_panel_api_health?: boolean;

    [key: string]: boolean | undefined;
  };
}

interface ConfigContextType {
  config: UIConfig | null;
  updateConfig: (section: string, key: string, value: any) => Promise<void>;
  refreshConfig: () => Promise<void>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

const DEFAULT_CONFIG: UIConfig = {
  titles: {
    app_title: 'Project Prahlada',
    app_subtitle: 'Social Media Analytics Dashboard',
    home_tab: 'होम (Home)',
    review_tab: 'समीक्षा (Review)',
    analytics_tab: 'एनालिटिक्स (Analytics)',
    control_hub_tab: 'कंट्रोल हब (Control Hub)'
  },
  modules: {
    // Home
    home_header: true,
    home_filters: true,
    home_table: true,

    // Review
    review_header: true,
    review_queue: true,
    review_ai_assistant: true,
    review_semantic_search: true,
    review_metrics: true,

    // Analytics
    analytics_header: true,
    analytics_summary: true,
    analytics_geo: true,
    analytics_tour: true,
    analytics_development: true,
    analytics_outreach: true,
    analytics_schemes: true,
    analytics_target_groups: true,
    analytics_thematic: true,
    analytics_raigarh: true,

    // Control Hub
    controlhub_header_systemhealth: true,
    controlhub_grid_analytics_sync: true,
    controlhub_panel_title_editor: true,
    controlhub_panel_api_health: true,
  }
};

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<UIConfig | null>(DEFAULT_CONFIG);

  const refreshConfig = async () => {
    try {
      const data = await apiService.get('/api/config') as Partial<UIConfig>;
      // Deep merge with defaults to ensure all keys exist
      setConfig({
        titles: { ...DEFAULT_CONFIG.titles, ...(data.titles || {}) },
        modules: { ...DEFAULT_CONFIG.modules, ...(data.modules || {}) }
      });
    } catch (error) {
      console.error("Failed to load config", error);
      setConfig(DEFAULT_CONFIG);
    }
  };

  const updateConfig = async (section: string, key: string, value: any) => {
    try {
      await apiService.post('/api/config', { section, key, value });
      await refreshConfig();
    } catch (error) {
      console.error("Failed to update config", error);
    }
  };

  useEffect(() => {
    refreshConfig();
  }, []);

  return (
    <ConfigContext.Provider value={{ config, updateConfig, refreshConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};
