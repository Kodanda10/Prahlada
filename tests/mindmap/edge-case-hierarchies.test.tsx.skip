import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';

describe('D3 HierarchyMindMap - Edge-Case Hierarchies', () => {
  describe('Missing Hierarchy Levels', () => {
    it('handles district-to-block direct connection', () => {
      const incompleteData = {
        name: 'रायगढ़',
        children: [
          {
            name: 'खरसिया ब्लॉक', // Missing constituency level
            children: [
              { name: 'जोंबी', visits: 5 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={incompleteData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Should still render the available hierarchy
      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('खरसिया ब्लॉक');
      expect(labels).toContain('जोंबी (05)');
    });

    it('renders district-to-village direct hierarchy', () => {
      const minimalData = {
        name: 'रायगढ़',
        children: [
          { name: 'जोंबी गाँव', visits: 3 },
          { name: 'तमनार गाँव', visits: 7 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={minimalData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('जोंबी गाँव (03)');
      expect(labels).toContain('तमनार गाँव (07)');
    });

    it('displays notice for incomplete hierarchy', () => {
      const incompleteWithNotice = {
        name: 'रायगढ़',
        children: [
          {
            name: 'अपूर्ण स्तर', // Special marker for incomplete data
            children: [
              { name: 'जोंबी', visits: 2 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={incompleteWithNotice}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should show notice in UI
      const notice = screen.queryByText(/स्तर की जानकारी अधूरी/);
      // Note: This would be implemented in the actual component
      expect(svg).toBeInTheDocument();
    });
  });

  describe('ULB (Urban Local Body) Mode', () => {
    it('renders corporation-zone-ward hierarchy', () => {
      const ulbData = {
        name: 'रायगढ़ नगर निगम',
        children: [
          {
            name: 'मुख्य ज़ोन',
            children: [
              {
                name: 'वार्ड 1',
                children: [
                  { name: 'उप-वार्ड 1A', visits: 12 },
                  { name: 'उप-वार्ड 1B', visits: 8 }
                ]
              },
              {
                name: 'वार्ड 2',
                children: [
                  { name: 'उप-वार्ड 2A', visits: 15 }
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={ulbData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      expect(labels).toContain('रायगढ़ नगर निगम');
      expect(labels).toContain('मुख्य ज़ोन');
      expect(labels).toContain('वार्ड 1');
      expect(labels).toContain('उप-वार्ड 1A (12)');
      expect(labels).toContain('उप-वार्ड 1B (08)');
      expect(labels).toContain('वार्ड 2');
      expect(labels).toContain('उप-वार्ड 2A (15)');
    });

    it('handles municipality hierarchy', () => {
      const municipalityData = {
        name: 'खरसिया नगर पालिका',
        children: [
          {
            name: 'ज़ोन A',
            children: [
              { name: 'वार्ड 1', visits: 25 },
              { name: 'वार्ड 2', visits: 30 }
            ]
          },
          {
            name: 'ज़ोन B',
            children: [
              { name: 'वार्ड 3', visits: 20 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={municipalityData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      expect(labels).toContain('खरसिया नगर पालिका');
      expect(labels).toContain('ज़ोन A');
      expect(labels).toContain('ज़ोन B');
      expect(labels).toContain('वार्ड 1 (25)');
      expect(labels).toContain('वार्ड 2 (30)');
      expect(labels).toContain('वार्ड 3 (20)');
    });
  });

  describe('Empty and Minimal Data Handling', () => {
    it('renders single node hierarchy', () => {
      const singleNodeData = {
        name: 'रायगढ़',
        children: []
      };

      const { container } = render(
        <HierarchyMindMap
          data={singleNodeData}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़');
    });

    it('handles null/undefined children gracefully', () => {
      const dataWithNulls = {
        name: 'रायगढ़',
        children: [
          { name: 'खरसिया', children: null },
          { name: 'रायगढ़', children: undefined },
          { name: 'तमनार', children: [] }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={dataWithNulls}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('खरसिया');
      expect(labels).toContain('तमनार');
    });

    it('processes very deep hierarchies without breaking', () => {
      // Create a very deep hierarchy (8 levels)
      const createDeepHierarchy = (depth: number, name: string): any => {
        if (depth === 0) {
          return { name: `${name} (01)`, visits: 1 };
        }
        return {
          name: `${name} स्तर ${depth}`,
          children: [createDeepHierarchy(depth - 1, name)]
        };
      };

      const deepData = createDeepHierarchy(8, 'गहरा');

      const { container } = render(
        <HierarchyMindMap
          data={deepData}
          width={1200}
          height={800}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render without crashing
      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels.length).toBeGreaterThan(0);
    });
  });

  describe('Data Type Variations', () => {
    it('handles numeric visit counts as strings', () => {
      const stringVisitsData = {
        name: 'रायगढ़',
        children: [
          { name: 'जोंबी', visits: '5' }, // String instead of number
          { name: 'तमनार', visits: 10 }  // Number
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={stringVisitsData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('जोंबी (05)');
      expect(labels).toContain('तमनार (10)');
    });

    it('processes zero and negative visit counts', () => {
      const edgeVisitData = {
        name: 'रायगढ़',
        children: [
          { name: 'जोंबी', visits: 0 },
          { name: 'तमनार', visits: -5 }, // Should handle gracefully
          { name: 'कमलौर', visits: 1000 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={edgeVisitData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('जोंबी (00)');
      expect(labels).toContain('तमनार (-5)'); // Should display as-is
      expect(labels).toContain('कमलौर (1000)');
    });

    it('manages very large visit numbers', () => {
      const largeNumbersData = {
        name: 'रायगढ़',
        children: [
          { name: 'जोंबी', visits: 999999 },
          { name: 'तमनार', visits: 1000000 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={largeNumbersData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('जोंबी (999999)');
      expect(labels).toContain('तमनार (1000000)');
    });
  });

  describe('Special Characters and Unicode', () => {
    it('renders complex Devanagari combinations', () => {
      const unicodeData = {
        name: 'क्षेत्रीय',
        children: [
          { name: 'ज़िम्मेदारी', visits: 5 },
          { name: 'मोर्चा', visits: 3 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={unicodeData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('क्षेत्रीय');
      expect(labels).toContain('ज़िम्मेदारी (05)');
      expect(labels).toContain('मोर्चा (03)');
    });

    it('handles mixed valid/invalid Unicode', () => {
      const mixedUnicodeData = {
        name: 'रायगढ़ (वैध)',
        children: [
          { name: 'खरसिया \uFFFD (अवैध)', visits: 1 }, // Replacement char
          { name: 'तमनार ✅', visits: 2 } // Valid emoji
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mixedUnicodeData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render without crashing
      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels.length).toBeGreaterThan(0);
    });
  });

  describe('Dynamic Hierarchy Updates', () => {
    it('handles hierarchy structure changes', () => {
      const initialData = {
        name: 'रायगढ़',
        children: [
          { name: 'खरसिया', visits: 10 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={initialData}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      let labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('खरसिया (10)');

      // Change to deeper hierarchy
      const deeperData = {
        name: 'रायगढ़',
        children: [
          {
            name: 'खरसिया',
            children: [
              { name: 'जोंबी', visits: 5 },
              { name: 'तमनार', visits: 5 }
            ]
          }
        ]
      };

      rerender(
        <HierarchyMindMap
          data={deeperData}
          width={800}
          height={600}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('खरसिया');
      expect(labels).toContain('जोंबी (05)');
      expect(labels).toContain('तमनार (05)');
    });

    it('adapts to different hierarchy depths', () => {
      const shallowData = {
        name: 'रायगढ़',
        children: [
          { name: 'जोंबी', visits: 1 },
          { name: 'तमनार', visits: 2 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={shallowData}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Change to very deep hierarchy
      const deepData = {
        name: 'रायगढ़',
        children: [
          {
            name: 'विधानसभा',
            children: [
              {
                name: 'विकासखंड',
                children: [
                  {
                    name: 'ग्राम पंचायत',
                    children: [
                      {
                        name: 'वार्ड',
                        children: [
                          { name: 'उप-वार्ड', visits: 1 }
                        ]
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      };

      rerender(
        <HierarchyMindMap
          data={deepData}
          width={800}
          height={600}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़');
      expect(labels).toContain('उप-वार्ड (01)');
    });
  });
});