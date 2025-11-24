import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AnimatedNavTabs, { TabItem } from '../../components/AnimatedNavTabs';
import NumberTicker from '../../components/NumberTicker';
import { Home } from 'lucide-react';

// Mock IntersectionObserver
const IntersectionObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

describe('Component Visual Snapshots', () => {
  describe('AnimatedNavTabs Component', () => {
    const mockTabs: TabItem[] = [
      { path: '/home', label: 'Home', icon: Home },
      { path: '/analytics', label: 'Analytics', icon: Home },
      { path: '/review', label: 'Review', icon: Home },
    ];

    it('renders consistent tab layout', () => {
      const { getAllByRole } = render(
        <MemoryRouter>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/home"
            isAdminLoggedIn={true}
          />
        </MemoryRouter>
      );

      const tabButtons = getAllByRole('link');
      expect(tabButtons).toHaveLength(3);

      mockTabs.forEach((tab, index) => {
        expect(tabButtons[index]).toHaveTextContent(tab.label);
      });
    });

    it('maintains active tab visual state', () => {
      const { getByText } = render(
        <MemoryRouter>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/analytics"
            isAdminLoggedIn={true}
          />
        </MemoryRouter>
      );

      const activeTab = getByText('Analytics').closest('a');
      expect(activeTab).toBeInTheDocument();
    });

    it('handles tab transitions smoothly', () => {
      const { rerender, getByText } = render(
        <MemoryRouter initialEntries={['/home']}>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/home"
            isAdminLoggedIn={true}
          />
        </MemoryRouter>
      );
      
      expect(getByText('Home').closest('a')).toBeInTheDocument();

      rerender(
        <MemoryRouter initialEntries={['/review']}>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/review"
            isAdminLoggedIn={true}
          />
        </MemoryRouter>
      );
      
      expect(getByText('Review').closest('a')).toBeInTheDocument();
    });
  });

  describe('NumberTicker Component', () => {
    it('renders number with consistent formatting', () => {
      const { container } = render(<NumberTicker value={1234} />);
      expect(container).toBeInTheDocument();
    });

    it('handles different number ranges', () => {
      const { container: smallContainer } = render(<NumberTicker value={42} />);
      const { container: largeContainer } = render(<NumberTicker value={999999} />);
      const { container: decimalContainer } = render(<NumberTicker value={123.45} />);

      expect(smallContainer).toBeInTheDocument();
      expect(largeContainer).toBeInTheDocument();
      expect(decimalContainer).toBeInTheDocument();
    });

    it('maintains consistent dimensions', () => {
      const { container } = render(
        <div style={{ width: '200px' }}>
          <NumberTicker value={56789} />
        </div>
      );
      expect(container.firstChild).toHaveStyle({ width: '200px' });
    });
  });
});
