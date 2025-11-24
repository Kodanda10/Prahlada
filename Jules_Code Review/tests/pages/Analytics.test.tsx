import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AnalyticsDashboard from '../../pages/Analytics';

// Mock IntersectionObserver
const IntersectionObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

describe('Analytics Dashboard', () => {
  it('renders all 9 sections with Hindi titles', () => {
    render(<AnalyticsDashboard />);
    
    // Check for main section titles in Hindi
    expect(screen.getByText('इवेंट प्रकार विश्लेषण')).toBeInTheDocument();
    expect(screen.getByText('भू-मानचित्रण एवं कवरेज')).toBeInTheDocument();
    expect(screen.getByText('टूर कवरेज विश्लेषण')).toBeInTheDocument();
    expect(screen.getByText('विकास कार्य विश्लेषण')).toBeInTheDocument();
    expect(screen.getByText('समाज आधारित पहुँच')).toBeInTheDocument();
    expect(screen.getByText('योजना विश्लेषण')).toBeInTheDocument();
    expect(screen.getByText('लक्षित वर्ग विश्लेषण')).toBeInTheDocument();
    expect(screen.getByText('विषयगत विश्लेषण')).toBeInTheDocument();
    expect(screen.getByText('रायगढ़ विधानसभा')).toBeInTheDocument();
  });

  it('renders filter dropdowns in Hindi', () => {
    render(<AnalyticsDashboard />);
    expect(screen.getByText('📍 सभी स्थान')).toBeInTheDocument();
    expect(screen.getByText('📑 सभी विषय')).toBeInTheDocument();
  });
});
