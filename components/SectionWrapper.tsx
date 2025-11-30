import React from 'react';
import { useConfig } from '../contexts/ConfigContext';

interface SectionWrapperProps {
    id: string;
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

const SectionWrapper: React.FC<SectionWrapperProps> = ({ id, children, fallback = null }) => {
    const { config } = useConfig();

    // If config is not loaded yet, render children (optimistic) or null? 
    // Let's render children to avoid flickering if config takes time, 
    // UNLESS we want to be strict. 
    // Better: if config is null, render null (loading).
    if (!config) return null;

    // Check if module is explicitly disabled
    if (config.modules[id] === false) {
        return <>{fallback}</>;
    }

    return <>{children}</>;
};

export default SectionWrapper;
