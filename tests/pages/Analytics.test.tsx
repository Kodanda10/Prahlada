
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AnalyticsDashboard from '../../pages/Analytics';

describe('Analytics Dashboard', () => {
  it('renders all 9 sections with Hindi titles', () => {
    const { getByText } = render(<AnalyticsDashboard />);
    
    // Check for main section titles in Hindi
    expect(getByText('इवेंट प्रकार विश्लेषण')).toBeInTheDocument();
    expect(getByText('भू-मानचित्रण एवं कवरेज')).toBeInTheDocument();
    expect(getByText('टूर कवरेज विश्लेषण')).toBeInTheDocument();
    expect(getByText('विकास कार्य विश्लेषण')).toBeInTheDocument();
    expect(getByText('समाज आधारित पहुँच')).toBeInTheDocument();
    expect(getByText('योजना विश्लेषण')).toBeInTheDocument();
    expect(getByText('लक्षित वर्ग विश्लेषण')).toBeInTheDocument();
    expect(getByText('विषयगत विश्लेषण')).toBeInTheDocument();
    expect(getByText('रायगढ़ विधानसभा')).toBeInTheDocument();
  });

  it('renders filter dropdowns in Hindi', () => {
    const { getByText } = render(<AnalyticsDashboard />);
    expect(getByText('📍 सभी स्थान')).toBeInTheDocument();
    expect(getByText('📑 सभी विषय')).toBeInTheDocument();
  });
});
