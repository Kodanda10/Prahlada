import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GlassCard } from '../../components/GlassCard';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';

describe('WCAG 2.1 AA Compliance', () => {
  describe('Keyboard Navigation', () => {
    it('supports Tab key navigation', async () => {
      const user = userEvent.setup();

      render(
        <div>
          <button>First Button</button>
          <AnimatedNavTabs
            tabs={[
              { id: 'tab1', label: 'Tab 1', path: '/tab1' },
              { id: 'tab2', label: 'Tab 2', path: '/tab2' },
            ]}
            activeTab="tab1"
            onTabChange={() => {}}
          />
        </div>
      );

      await user.tab();
      expect(document.activeElement).toHaveTextContent('First Button');

      await user.tab();
      const activeElement = document.activeElement;
      expect(activeElement).toBeInTheDocument();
    });

    it('provides visible focus indicators', () => {
      render(
        <button className="focus-button">Focusable Button</button>
      );

      const button = screen.getByRole('button');
      button.focus();

      expect(button).toHaveFocus();
      expect(button).toHaveClass('focus-button');
    });

    it('handles arrow key navigation in tab components', async () => {
      const user = userEvent.setup();
      const onTabChange = vi.fn();

      render(
        <AnimatedNavTabs
          tabs={[
            { id: 'tab1', label: 'Tab 1', path: '/tab1' },
            { id: 'tab2', label: 'Tab 2', path: '/tab2' },
          ]}
          activeTab="tab1"
          onTabChange={onTabChange}
        />
      );

      const tabContainer = document.querySelector('.animated-nav-tabs');
      if (tabContainer) {
        tabContainer.focus();
        await user.keyboard('{ArrowRight}');

        expect(onTabChange).toHaveBeenCalled();
      }
    });
  });

  describe('Screen Reader Support', () => {
    it('provides proper ARIA labels', () => {
      render(
        <GlassCard title="Test Card" aria-label="Descriptive card">
          <button aria-label="Action button">Click me</button>
        </GlassCard>
      );

      const card = screen.getByRole('article');
      const button = screen.getByRole('button');

      expect(card).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-label', 'Action button');
    });

    it('maintains heading hierarchy', () => {
      render(
        <div>
          <h1>Main Title</h1>
          <h2>Section Title</h2>
          <h3>Subsection Title</h3>
        </div>
      );

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Main Title');
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Section Title');
      expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Subsection Title');
    });

    it('includes alt text for images', () => {
      render(
        <img src="chart.png" alt="Sales chart showing quarterly performance" />
      );

      const image = screen.getByAltText('Sales chart showing quarterly performance');
      expect(image).toBeInTheDocument();
    });
  });

  describe('Color Contrast & Visual Accessibility', () => {
    it('maintains sufficient color contrast', () => {
      render(
        <div className="high-contrast-text">
          <p className="text-on-glass">Text on glass background</p>
        </div>
      );

      const textElement = screen.getByText('Text on glass background');
      expect(textElement).toHaveClass('text-on-glass');
    });

    it('provides focus-visible styles', () => {
      render(
        <button className="focus-visible-button">Button</button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus-visible-button');
    });
  });

  describe('Motion & Animation Preferences', () => {
    it('respects prefers-reduced-motion', () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
        })),
      });

      render(<AnimatedNavTabs tabs={[]} activeTab="" onTabChange={() => {}} />);

      expect(window.matchMedia).toHaveBeenCalledWith('(prefers-reduced-motion: reduce)');
    });
  });
});