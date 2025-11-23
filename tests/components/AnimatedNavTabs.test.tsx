
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import AnimatedNavTabs, { TabItem } from '../../components/AnimatedNavTabs';
import { Home } from 'lucide-react';

const MOCK_TABS: TabItem[] = [
  { path: '/', label: 'Test Home', icon: Home },
  { path: '/protected', label: 'Protected', icon: Home, protected: true }
];

describe('AnimatedNavTabs', () => {
  it('renders visible tabs', () => {
    const { getByText } = render(
      <BrowserRouter>
        <AnimatedNavTabs 
          tabs={MOCK_TABS} 
          activePath="/" 
          isAuthenticated={true} 
        />
      </BrowserRouter>
    );
    expect(getByText('Test Home')).toBeInTheDocument();
    expect(getByText('Protected')).toBeInTheDocument();
  });

  it('hides protected tabs when logged out', () => {
    const { getByText, queryByText } = render(
      <BrowserRouter>
        <AnimatedNavTabs 
          tabs={MOCK_TABS} 
          activePath="/" 
          isAuthenticated={false} 
        />
      </BrowserRouter>
    );
    expect(getByText('Test Home')).toBeInTheDocument();
    expect(queryByText('Protected')).not.toBeInTheDocument();
  });
});
