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
    [key: string]: boolean;
  };
}

interface ConfigContextType {
  config: UIConfig | null;
  updateConfig: (section: string, key: string, value: any) => Promise<void>;
  refreshConfig: () => Promise<void>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<UIConfig | null>(null);

  const refreshConfig = async () => {
    try {
      const data = await apiService.get('/config');
      setConfig(data);
    } catch (error) {
      console.error("Failed to load config", error);
    }
  };

  const updateConfig = async (section: string, key: string, value: any) => {
    try {
      await apiService.post('/config', { section, key, value });
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
