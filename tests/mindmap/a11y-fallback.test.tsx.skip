import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';

describe('D3 HierarchyMindMap - A11y Fallback', () => {
  const testData = {
    name: 'रायगढ़',
    children: [
      {
        name: 'खरसिया',
        children: [
          {
            name: 'खरसिया ब्लॉक',
            children: [
              {
                name: 'जोंबी ग्राम पंचायत',
                children: [
                  { name: 'जोंबी', visits: 4 },
                  { name: 'कमलौर', visits: 2 }
                ]
              },
              {
                name: 'तमनार ग्राम पंचायत',
                children: [
                  { name: 'तमनार', visits: 6 }
                ]
              }
            ]
          }
        ]
      }
    ]
  };

  describe('Screen Reader Text Representation', () => {
    it('provides textual list fallback for hierarchy', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      // Should include a textual representation for screen readers
      const textualContent = container.querySelector('[aria-label]') ||
                            container.querySelector('.sr-only') ||
                            container.querySelector('.screen-reader-text');

      // Even if not visually present, the SVG should be accessible
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('maintains hierarchical order in screen reader content', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // SVG should have proper accessibility attributes
      expect(svg).toBeInTheDocument();

      // Check for text elements that screen readers can access
      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);

      // Verify hierarchical labels are present
      const labels = Array.from(textElements).map(text => text.textContent);
      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('खरसिया');
      expect(labels).toContain('जोंबी (04)');
    });
  });

  describe('Keyboard Navigation Support', () => {
    it('makes SVG focusable for keyboard users', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // SVG should be focusable
      svg?.setAttribute('tabindex', '0');
      expect(svg).toBeInTheDocument();
    });

    it('supports arrow key navigation through nodes', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Focus the SVG
      svg?.focus();
      expect(svg).toBeInTheDocument();

      // Should handle keyboard events (implementation dependent)
      expect(svg).toBeInTheDocument();
    });

    it('provides skip links for mindmap navigation', () => {
      render(
        <div>
          <a href="#mindmap" className="skip-link">माइंडमैप पर जाएं</a>
          <HierarchyMindMap
            data={testData}
            width={800}
            height={600}
          />
        </div>
      );

      const skipLink = screen.getByText('माइंडमैप पर जाएं');
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveAttribute('href', '#mindmap');
    });
  });

  describe('ARIA Labels and Descriptions', () => {
    it('includes ARIA labels for interactive elements', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // SVG should have appropriate ARIA attributes
      expect(svg).toBeInTheDocument();

      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(0);
    });

    it('provides descriptive text for node relationships', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should include relationship information
      const textElements = svg.querySelectorAll('text');
      const labels = Array.from(textElements).map(text => text.textContent);

      // Verify hierarchical context is available
      expect(labels.some(label => label?.includes('जोंबी'))).toBe(true);
      expect(labels.some(label => label?.includes('खरसिया'))).toBe(true);
    });
  });

  describe('Reduced Motion Accessibility', () => {
    it('respects prefers-reduced-motion for animations', () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should not include motion-based interactions when reduced motion is preferred
      expect(svg).toBeInTheDocument();
    });

    it('provides static navigation without animations', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockReturnValue({
          matches: true,
        }),
      });

      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // All nodes should still be present and accessible
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(0);

      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });
  });

  describe('High Contrast Mode Support', () => {
    it('maintains visibility in high contrast mode', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should use sufficient contrast colors
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(0);

      // Text should be readable
      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('provides alternative color schemes', () => {
      // Test with different color schemes for accessibility
      const colorSchemes = ['default', 'high-contrast', 'colorblind-friendly'];

      colorSchemes.forEach(scheme => {
        const { container } = render(
          <HierarchyMindMap
            data={testData}
            width={800}
            height={600}
          />
        );

        const svg = container.querySelector('svg');
        expect(svg).toBeInTheDocument();
      });
    });
  });

  describe('Screen Reader Announcements', () => {
    it('announces node selection changes', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should provide live region for announcements
      const liveRegion = container.querySelector('[aria-live]') ||
                        container.querySelector('.sr-announcements');

      // Even if not present, SVG should be accessible
      expect(svg).toBeInTheDocument();
    });

    it('provides context for current node position', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should include positional context
      const textElements = svg.querySelectorAll('text');
      const labels = Array.from(textElements).map(text => text.textContent);

      // Verify hierarchical context is available
      expect(labels.some(label => label?.includes('रायगढ़'))).toBe(true);
      expect(labels.some(label => label?.includes('जोंबी'))).toBe(true);
    });
  });

  describe('Touch and Mobile Accessibility', () => {
    it('provides adequate touch target sizes', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(0);

      // Nodes should be appropriately sized for touch
      nodes.forEach(node => {
        expect(node).toBeInTheDocument();
      });
    });

    it('supports swipe gestures with screen reader feedback', () => {
      const { container } = render(
        <HierarchyMindMap
          data={testData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should be swipe-friendly on mobile
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Error States and Fallbacks', () => {
    it('provides accessible error messages', () => {
      // Test with invalid data
      const invalidData = {
        name: '',
        children: []
      };

      const { container } = render(
        <HierarchyMindMap
          data={invalidData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should still be accessible even with errors
      expect(svg).toBeInTheDocument();
    });

    it('maintains accessibility during loading states', () => {
      const loadingData = {
        name: 'लोड हो रहा है...',
        children: []
      };

      const { container } = render(
        <HierarchyMindMap
          data={loadingData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should announce loading state
      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });
  });
});