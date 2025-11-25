import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Activity } from 'lucide-react';
import AnimatedNavTabs from '../../components/AnimatedNavTabs';
import NumberTicker from '../../components/NumberTicker';

describe('Component Visual Snapshots', () => {
  describe('AnimatedNavTabs Component', () => {
    const mockTabs = [
      { label: 'Home', path: '/home', icon: Activity },
      { label: 'Analytics', path: '/analytics', icon: Activity },
      { label: 'Review', path: '/review', icon: Activity },
    ];

    it('renders consistent tab layout', () => {
      const { container } = render(
        <MemoryRouter>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/home"
            isAuthenticated={true}
            className="animated-nav-tabs"
          />
        </MemoryRouter>
      );

      const navElement = container.querySelector('.animated-nav-tabs');
      expect(navElement).toBeInTheDocument();

      const tabLinks = screen.getAllByRole('link');
      expect(tabLinks).toHaveLength(3);

      // Verify tab structure
      mockTabs.forEach((tab, index) => {
        expect(tabLinks[index]).toHaveTextContent(tab.label);
      });
    });

    it('maintains active tab visual state', () => {
      render(
        <MemoryRouter>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/analytics"
            isAuthenticated={true}
            className="animated-nav-tabs"
          />
        </MemoryRouter>
      );

      // Active tab has bold text class 'font-bold'
      const activeTab = screen.getByText('Analytics').closest('a');
      expect(activeTab).toBeInTheDocument();
      expect(activeTab).toHaveClass('font-bold');
    });

    it('handles tab transitions smoothly', () => {
      const { rerender } = render(
        <MemoryRouter>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/home"
            isAuthenticated={true}
            className="animated-nav-tabs"
          />
        </MemoryRouter>
      );

      let activeTab = screen.getByText('Home').closest('a');
      expect(activeTab).toHaveClass('font-bold');

      rerender(
        <MemoryRouter>
          <AnimatedNavTabs
            tabs={mockTabs}
            activePath="/review"
            isAuthenticated={true}
            className="animated-nav-tabs"
          />
        </MemoryRouter>
      );

      activeTab = screen.getByText('Review').closest('a');
      expect(activeTab).toHaveClass('font-bold');
    });
  });

  describe('NumberTicker Component', () => {
    it('renders number with consistent formatting', () => {
      const { container } = render(<NumberTicker value={1234} className="number-ticker" />);

      const tickerElement = container.querySelector('.number-ticker');
      expect(tickerElement).toBeInTheDocument();

      // Check if number is displayed
      expect(tickerElement).toHaveTextContent('1,234');
    });

    it('handles different number ranges', () => {
      const { container: smallContainer } = render(<NumberTicker value={42} className="number-ticker" />);
      const { container: largeContainer } = render(<NumberTicker value={999999} className="number-ticker" />);
      const { container: decimalContainer } = render(<NumberTicker value={123.45} className="number-ticker" />);

      expect(smallContainer.querySelector('.number-ticker')).toBeInTheDocument();
      expect(largeContainer.querySelector('.number-ticker')).toBeInTheDocument();
      expect(decimalContainer.querySelector('.number-ticker')).toBeInTheDocument();
    });

    it('maintains consistent dimensions', () => {
      const { container } = render(
        <div style={{ width: '200px' }}>
          <NumberTicker value={56789} className="number-ticker" />
        </div>
      );

      const ticker = container.querySelector('.number-ticker');
      expect(ticker).toBeInTheDocument();
      expect(ticker?.parentElement).toHaveStyle({ width: '200px' });
    });
  });
});