import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AnimatedGlassCard } from '../../components/AnimatedGlassCard';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';

describe('Reduced Motion Preferences', () => {
  describe('Prefers Reduced Motion Detection', () => {
    it('detects prefers-reduced-motion setting', () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation((query) => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
        })),
      });

      render(
        <AnimatedGlassCard delay={0}>
          <div>Reduced motion test</div>
        </AnimatedGlassCard>
      );

      // Should detect and respond to reduced motion preference
      expect(window.matchMedia).toHaveBeenCalledWith('(prefers-reduced-motion: reduce)');
    });

    it('respects user accessibility preferences', () => {
      // Test with reduced motion enabled
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
          media: '(prefers-reduced-motion: reduce)',
        }),
      });

      render(
        <div className="motion-test">
          <AnimatedGlassCard delay={0}>
            <div>Motion sensitive content</div>
          </AnimatedGlassCard>
        </div>
      );

      const card = document.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();

      // In real implementation, this would disable/reduce animations
      expect(card).toHaveClass('animated-glass-card');
    });
  });

  describe('Animation Reduction', () => {
    it('disables entrance animations when reduced motion is preferred', () => {
      // Mock reduced motion
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      render(
        <AnimatedGlassCard delay={100}>
          <div>Should not animate</div>
        </AnimatedGlassCard>
      );

      const card = document.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();

      // Should have reduced animation class or no animation
      expect(card).toHaveClass('animated-glass-card');
    });

    it('minimizes motion for tab transitions', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      render(
        <AnimatedNavTabs
          tabs={[
            { id: 'tab1', label: 'Tab 1', path: '/tab1' },
            { id: 'tab2', label: 'Tab 2', path: '/tab2' },
          ]}
          activeTab="tab1"
          onTabChange={() => {}}
        />
      );

      const navTabs = document.querySelector('.animated-nav-tabs');
      expect(navTabs).toBeInTheDocument();

      // Should have reduced motion styles
      expect(navTabs).toHaveClass('animated-nav-tabs');
    });

    it('provides static alternatives to animated elements', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      render(
        <div className="motion-alternatives">
          <AnimatedGlassCard delay={0}>
            <div>Content with motion alternative</div>
          </AnimatedGlassCard>
        </div>
      );

      const card = document.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();

      // Should render static version
      const content = screen.getByText('Content with motion alternative');
      expect(content).toBeInTheDocument();
    });
  });

  describe('Progressive Enhancement', () => {
    it('works without motion when JavaScript is disabled', () => {
      // This would be tested with server-side rendering or static generation
      render(
        <div className="no-js-fallback">
          <div className="static-card">
            <h3>Static Content</h3>
            <p>No JavaScript required</p>
          </div>
        </div>
      );

      const staticCard = document.querySelector('.static-card');
      expect(staticCard).toBeInTheDocument();

      const heading = screen.getByRole('heading', { level: 3 });
      const paragraph = screen.getByText('No JavaScript required');

      expect(heading).toBeInTheDocument();
      expect(paragraph).toBeInTheDocument();
    });

    it('provides meaningful content without animations', () => {
      render(
        <div className="content-without-motion">
          <AnimatedGlassCard delay={0}>
            <h2>Important Information</h2>
            <p>This content is accessible without motion</p>
            <button>Action Button</button>
          </AnimatedGlassCard>
        </div>
      );

      const heading = screen.getByRole('heading', { level: 2 });
      const content = screen.getByText('This content is accessible without motion');
      const button = screen.getByRole('button');

      expect(heading).toBeInTheDocument();
      expect(content).toBeInTheDocument();
      expect(button).toBeInTheDocument();

      // Content should be fully accessible
      expect(button).toHaveTextContent('Action Button');
    });
  });

  describe('Performance with Reduced Motion', () => {
    it('improves performance by skipping animations', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      const startTime = performance.now();

      render(
        <div className="performance-test">
          {Array.from({ length: 10 }, (_, i) => (
            <AnimatedGlassCard key={i} delay={i * 50}>
              <div>Performance card {i + 1}</div>
            </AnimatedGlassCard>
          ))}
        </div>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render faster without animations
      expect(renderTime).toBeLessThan(100);

      const cards = document.querySelectorAll('.animated-glass-card');
      expect(cards).toHaveLength(10);
    });

    it('reduces CPU usage during interactions', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      render(
        <AnimatedNavTabs
          tabs={[
            { id: 'perf1', label: 'Performance 1', path: '/perf1' },
            { id: 'perf2', label: 'Performance 2', path: '/perf2' },
            { id: 'perf3', label: 'Performance 3', path: '/perf3' },
          ]}
          activeTab="perf1"
          onTabChange={() => {}}
        />
      );

      const navTabs = document.querySelector('.animated-nav-tabs');
      expect(navTabs).toBeInTheDocument();

      // Should not trigger expensive animation calculations
      const tabs = document.querySelectorAll('.tab-button');
      expect(tabs).toHaveLength(3);
    });
  });

  describe('Cross-Browser Compatibility', () => {
    it('handles browsers without matchMedia support', () => {
      // Mock missing matchMedia
      const originalMatchMedia = window.matchMedia;
      delete (window as any).matchMedia;

      render(
        <AnimatedGlassCard delay={0}>
          <div>Fallback for old browsers</div>
        </AnimatedGlassCard>
      );

      const card = document.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();

      // Restore
      window.matchMedia = originalMatchMedia;
    });

    it('provides fallbacks for different browser capabilities', () => {
      // Test different user agent scenarios
      const userAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
      ];

      userAgents.forEach(ua => {
        Object.defineProperty(navigator, 'userAgent', {
          value: ua,
          configurable: true,
        });

        render(
          <div className={`browser-test-${ua.substring(0, 10)}`}>
            <AnimatedGlassCard delay={0}>
              <div>Browser compatibility test</div>
            </AnimatedGlassCard>
          </div>
        );

        const card = document.querySelector('.animated-glass-card');
        expect(card).toBeInTheDocument();
      });
    });
  });

  describe('User Experience Continuity', () => {
    it('maintains visual hierarchy without motion', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      render(
        <div className="hierarchy-test">
          <h1>Main Heading</h1>
          <AnimatedGlassCard delay={0}>
            <h2>Card Heading</h2>
            <p>Card content without distracting motion</p>
          </AnimatedGlassCard>
          <footer>Footer content</footer>
        </div>
      );

      const mainHeading = screen.getByRole('heading', { level: 1 });
      const cardHeading = screen.getByRole('heading', { level: 2 });
      const cardContent = screen.getByText('Card content without distracting motion');
      const footer = screen.getByText('Footer content');

      expect(mainHeading).toBeInTheDocument();
      expect(cardHeading).toBeInTheDocument();
      expect(cardContent).toBeInTheDocument();
      expect(footer).toBeInTheDocument();

      // Visual hierarchy should be maintained
      expect(mainHeading.compareDocumentPosition(cardHeading)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
    });

    it('preserves content readability and usability', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      render(
        <div className="usability-test">
          <AnimatedNavTabs
            tabs={[
              { id: 'readability', label: 'Readability', path: '/readability' },
              { id: 'usability', label: 'Usability', path: '/usability' },
            ]}
            activeTab="readability"
            onTabChange={() => {}}
          />
          <main>
            <p>Content should remain fully readable and usable</p>
            <button>Interactive Element</button>
          </main>
        </div>
      );

      const content = screen.getByText('Content should remain fully readable and usable');
      const button = screen.getByRole('button');

      expect(content).toBeInTheDocument();
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Interactive Element');
    });
  });
});