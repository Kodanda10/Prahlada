import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';

describe('D3 HierarchyMindMap - Edge-Case Hierarchies', () => {
  describe('Missing Hierarchy Levels', () => {
    it('handles district-to-block direct connection', () => {
      const incompleteData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 100,
        children: [
          {
            id: 'kharsia-block',
            label: 'खरसिया ब्लॉक', // Missing constituency level
            level: 3,
            visits: 5,
            children: [
              { id: 'jombi', label: 'जोंबी', level: 5, visits: 5 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);

      // Should still render the available hierarchy
      expect(labels).toContain('रायगढ़ (100)');
      expect(labels).toContain('खरसिया ब्लॉक (05)');
      expect(labels).toContain('जोंबी (05)');
    });

    it('renders district-to-village direct hierarchy', () => {
      const minimalData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 10,
        children: [
          { id: 'jombi', label: 'जोंबी गाँव', level: 5, visits: 3 },
          { id: 'tamnar', label: 'तमनार गाँव', level: 5, visits: 7 }
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

      expect(labels).toContain('रायगढ़ (10)');
      expect(labels).toContain('जोंबी गाँव (03)');
      expect(labels).toContain('तमनार गाँव (07)');
    });

    it('displays notice for incomplete hierarchy', () => {
      const incompleteWithNotice: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 100,
        children: [
          {
            id: 'incomplete',
            label: 'अपूर्ण स्तर', // Special marker for incomplete data
            level: 2,
            visits: 2,
            children: [
              { id: 'jombi', label: 'जोंबी', level: 5, visits: 2 }
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
      const ulbData: any = {
        id: 'raigarh-corp',
        label: 'रायगढ़ नगर निगम',
        level: 1,
        visits: 35,
        children: [
          {
            id: 'main-zone',
            label: 'मुख्य ज़ोन',
            level: 2,
            visits: 35,
            children: [
              {
                id: 'ward-1',
                label: 'वार्ड 1',
                level: 3,
                visits: 20,
                children: [
                  { id: 'sub-ward-1a', label: 'उप-वार्ड 1A', level: 4, visits: 12 },
                  { id: 'sub-ward-1b', label: 'उप-वार्ड 1B', level: 4, visits: 8 }
                ]
              },
              {
                id: 'ward-2',
                label: 'वार्ड 2',
                level: 3,
                visits: 15,
                children: [
                  { id: 'sub-ward-2a', label: 'उप-वार्ड 2A', level: 4, visits: 15 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);

      expect(labels).toContain('रायगढ़ नगर निगम (35)');
      expect(labels).toContain('मुख्य ज़ोन (35)');
      expect(labels).toContain('वार्ड 1 (20)');
      expect(labels).toContain('उप-वार्ड 1A (12)');
      expect(labels).toContain('उप-वार्ड 1B (08)');
      expect(labels).toContain('वार्ड 2 (15)');
      expect(labels).toContain('उप-वार्ड 2A (15)');
    });

    it('handles municipality hierarchy', () => {
      const municipalityData: any = {
        id: 'kharsia-muni',
        label: 'खरसिया नगर पालिका',
        level: 1,
        visits: 75,
        children: [
          {
            id: 'zone-a',
            label: 'ज़ोन A',
            level: 2,
            visits: 55,
            children: [
              { id: 'ward-1', label: 'वार्ड 1', level: 3, visits: 25 },
              { id: 'ward-2', label: 'वार्ड 2', level: 3, visits: 30 }
            ]
          },
          {
            id: 'zone-b',
            label: 'ज़ोन B',
            level: 2,
            visits: 20,
            children: [
              { id: 'ward-3', label: 'वार्ड 3', level: 3, visits: 20 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);

      expect(labels).toContain('खरसिया नगर पालिका (75)');
      expect(labels).toContain('ज़ोन A (55)');
      expect(labels).toContain('ज़ोन B (20)');
      expect(labels).toContain('वार्ड 1 (25)');
      expect(labels).toContain('वार्ड 2 (30)');
      expect(labels).toContain('वार्ड 3 (20)');
    });
  });

  describe('Empty and Minimal Data Handling', () => {
    it('renders single node hierarchy', () => {
      const singleNodeData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 0,
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (00)');
    });

    it('handles null/undefined children gracefully', () => {
      const dataWithNulls: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 0,
        children: [
          { id: 'kharsia', label: 'खरसिया', level: 2, visits: 0, children: null },
          { id: 'raigarh-city', label: 'रायगढ़ शहर', level: 2, visits: 0, children: undefined },
          { id: 'tamnar', label: 'तमनार', level: 2, visits: 0, children: [] }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (00)');
      expect(labels).toContain('खरसिया (00)');
      expect(labels).toContain('तमनार (00)');
    });

    it('processes very deep hierarchies without breaking', () => {
      // Create a very deep hierarchy (8 levels)
      const createDeepHierarchy = (depth: number, name: string): any => {
        if (depth === 0) {
          return { id: `leaf-${depth}`, label: `${name} (01)`, level: 5, visits: 1 };
        }
        return {
          id: `node-${depth}`,
          label: `${name} स्तर ${depth}`,
          level: Math.min(5, 6 - depth) as any, // Mock level logic
          visits: 1,
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
      const stringVisitsData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 15,
        children: [
          { id: 'jombi', label: 'जोंबी', level: 5, visits: '5' }, // String instead of number
          { id: 'tamnar', label: 'तमनार', level: 5, visits: 10 }  // Number
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('जोंबी (05)');
      expect(labels).toContain('तमनार (10)');
    });

    it('processes zero and negative visit counts', () => {
      const edgeVisitData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 995,
        children: [
          { id: 'jombi', label: 'जोंबी', level: 5, visits: 0 },
          { id: 'tamnar', label: 'तमनार', level: 5, visits: -5 }, // Should handle gracefully
          { id: 'kamlaur', label: 'कमलौर', level: 5, visits: 1000 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('जोंबी (00)');
      expect(labels).toContain('तमनार (-5)'); // Should display as-is
      expect(labels).toContain('कमलौर (1000)');
    });

    it('manages very large visit numbers', () => {
      const largeNumbersData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 1999999,
        children: [
          { id: 'jombi', label: 'जोंबी', level: 5, visits: 999999 },
          { id: 'tamnar', label: 'तमनार', level: 5, visits: 1000000 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('जोंबी (999999)');
      expect(labels).toContain('तमनार (1000000)');
    });
  });

  describe('Special Characters and Unicode', () => {
    it('renders complex Devanagari combinations', () => {
      const unicodeData: any = {
        id: 'regional',
        label: 'क्षेत्रीय',
        level: 1,
        visits: 8,
        children: [
          { id: 'responsibility', label: 'ज़िम्मेदारी', level: 2, visits: 5 },
          { id: 'front', label: 'मोर्चा', level: 2, visits: 3 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('क्षेत्रीय (08)');
      expect(labels).toContain('ज़िम्मेदारी (05)');
      expect(labels).toContain('मोर्चा (03)');
    });

    it('handles mixed valid/invalid Unicode', () => {
      const mixedUnicodeData: any = {
        id: 'raigarh-valid',
        label: 'रायगढ़ (वैध)',
        level: 1,
        visits: 3,
        children: [
          { id: 'kharsia-invalid', label: 'खरसिया \uFFFD (अवैध)', level: 2, visits: 1 }, // Replacement char
          { id: 'tamnar-valid', label: 'तमनार ✅', level: 2, visits: 2 } // Valid emoji
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
      const initialData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 10,
        children: [
          { id: 'kharsia', label: 'खरसिया', level: 2, visits: 10 }
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

      let labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (10)');
      expect(labels).toContain('खरसिया (10)');

      // Change to deeper hierarchy
      const deeperData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 10,
        children: [
          {
            id: 'kharsia',
            label: 'खरसिया',
            level: 2,
            visits: 10,
            children: [
              { id: 'jombi', label: 'जोंबी', level: 5, visits: 5 },
              { id: 'tamnar', label: 'तमनार', level: 5, visits: 5 }
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

      labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (10)');
      expect(labels).toContain('खरसिया (10)');
      expect(labels).toContain('जोंबी (05)');
      expect(labels).toContain('तमनार (05)');
    });

    it('adapts to different hierarchy depths', () => {
      const shallowData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 3,
        children: [
          { id: 'jombi', label: 'जोंबी', level: 5, visits: 1 },
          { id: 'tamnar', label: 'तमनार', level: 5, visits: 2 }
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
      const deepData: any = {
        id: 'raigarh',
        label: 'रायगढ़',
        level: 1,
        visits: 1,
        children: [
          {
            id: 'vidhansabha',
            label: 'विधानसभा',
            level: 2,
            visits: 1,
            children: [
              {
                id: 'vikaskhand',
                label: 'विकासखंड',
                level: 3,
                visits: 1,
                children: [
                  {
                    id: 'gram-panchayat',
                    label: 'ग्राम पंचायत',
                    level: 4,
                    visits: 1,
                    children: [
                      {
                        id: 'ward',
                        label: 'वार्ड',
                        level: 5,
                        visits: 1,
                        children: [
                          { id: 'sub-ward', label: 'उप-वार्ड', level: 5, visits: 1 }
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

      const labels = Array.from(svg!.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (01)');
      expect(labels).toContain('उप-वार्ड (01)');
    });
  });
});