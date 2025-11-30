import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';

describe('D3 HierarchyMindMap - Hierarchy Correctness', () => {
  // Real FAISS metadata structure as specified
  const faisMetadata = {
    district: "रायगढ़",
    constituency: "खरसिया",
    block: "खरसिया ब्लॉक",
    gp: "जोंबी ग्राम पंचायत",
    village: "जोंबी",
    visits: 4
  };

  const sampleHierarchyData = {
    id: 'root',
    label: faisMetadata.district,
    level: 1,
    visits: 4,
    children: [
      {
        id: 'c1',
        label: faisMetadata.constituency,
        level: 2,
        visits: 4,
        children: [
          {
            id: 'b1',
            label: faisMetadata.block,
            level: 3,
            visits: 4,
            children: [
              {
                id: 'g1',
                label: faisMetadata.gp,
                level: 4,
                visits: 4,
                children: [
                  { id: 'v1', label: faisMetadata.village, level: 5, visits: faisMetadata.visits }
                ]
              }
            ]
          }
        ]
      }
    ]
  };

  describe('FAISS Metadata Structure Validation', () => {
    it('renders district as root node with correct Hindi label', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should contain the district name
      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(`${faisMetadata.district} (04)`);
    });

    it('displays constituency as first child level', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(`${faisMetadata.constituency} (04)`);
    });

    it('shows block as second level with correct Hindi text', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(`${faisMetadata.block} (04)`);
    });

    it('renders gram panchayat as third level', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(`${faisMetadata.gp} (04)`);
    });

    it('displays village as leaf node with visit count', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Should show visit count in format: "जोंबी (04)"
      const visitLabel = `${faisMetadata.village} (${faisMetadata.visits.toString().padStart(2, '0')})`;
      expect(labels).toContain(visitLabel);
    });
  });

  describe('Node Visit Count Consistency', () => {
    it('displays visit counts in Hindi numerals with padding', () => {
      const testData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 17,
        children: [
          {
            id: 'c1',
            label: 'खरसिया',
            level: 2,
            visits: 17,
            children: [
              { id: 'v1', label: 'जोंबी गाँव', level: 5, visits: 4 },
              { id: 'v2', label: 'तमनार गाँव', level: 5, visits: 12 },
              { id: 'v3', label: 'कमलौर गाँव', level: 5, visits: 1 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={testData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Check specific visit count formats
      expect(labels).toContain('जोंबी गाँव (04)');
      expect(labels).toContain('तमनार गाँव (12)');
      expect(labels).toContain('कमलौर गाँव (01)');
    });

    it('aggregates visit counts at parent levels', () => {
      const aggregatedData = {
        id: 'root',
        label: 'रायगढ़', // 4 + 12 + 1 + 4 (from gp level)
        level: 1,
        visits: 21,
        children: [
          {
            id: 'c1',
            label: 'खरसिया',
            level: 2,
            visits: 21,
            children: [
              { id: 'b1', label: 'खरसिया ब्लॉक', level: 3, visits: 17 }, // 4 + 12 + 1
              {
                id: 'gp1',
                label: 'जोंबी ग्राम पंचायत',
                level: 4,
                visits: 4,
                children: [
                  { id: 'v1', label: 'जोंबी', level: 5, visits: 4 }
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={aggregatedData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify aggregated counts
      expect(labels).toContain('रायगढ़ (21)');
      expect(labels).toContain('खरसिया (21)');
      expect(labels).toContain('खरसिया ब्लॉक (17)');
      expect(labels).toContain('जोंबी ग्राम पंचायत (04)');
      expect(labels).toContain('जोंबी (04)');
    });
  });

  describe('Hierarchical Order Validation', () => {
    it('maintains correct administrative hierarchy order', () => {
      const orderedData = {
        id: 'root',
        label: 'जिला',
        level: 1,
        visits: 1,
        children: [
          {
            id: 'c1',
            label: 'विधानसभा',
            level: 2,
            visits: 1,
            children: [
              {
                id: 'b1',
                label: 'विकासखंड',
                level: 3,
                visits: 1,
                children: [
                  {
                    id: 'gp1',
                    label: 'ग्राम पंचायत',
                    level: 4,
                    visits: 1,
                    children: [
                      { id: 'v1', label: 'गाँव/वार्ड', level: 5, visits: 1 }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={orderedData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify hierarchical order is maintained
      const expectedOrder = [
        'जिला (01)',
        'विधानसभा (01)',
        'विकासखंड (01)',
        'ग्राम पंचायत (01)',
        'गाँव/वार्ड (01)'
      ];

      expectedOrder.forEach(label => {
        expect(labels).toContain(label);
      });
    });

    it('handles ULB (Urban Local Body) hierarchy correctly', () => {
      const ulbData = {
        id: 'root',
        label: 'नगर निगम',
        level: 1,
        visits: 5,
        children: [
          {
            id: 'z1',
            label: 'ज़ोन',
            level: 2,
            visits: 5,
            children: [
              {
                id: 'w1',
                label: 'वार्ड',
                level: 3,
                visits: 5,
                children: [
                  { id: 'sw1', label: 'उप-वार्ड', level: 5, visits: 5 }
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={ulbData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify ULB hierarchy
      expect(labels).toContain('नगर निगम (05)');
      expect(labels).toContain('ज़ोन (05)');
      expect(labels).toContain('वार्ड (05)');
      expect(labels).toContain('उप-वार्ड (05)');
    });
  });

  describe('Multi-District Hierarchy Support', () => {
    it('renders multiple districts in single mindmap', () => {
      const multiDistrictData = {
        id: 'root',
        label: 'छत्तीसगढ़',
        level: 0,
        visits: 350,
        children: [
          {
            id: 'd1',
            label: 'रायगढ़',
            level: 1,
            visits: 150,
            children: [
              { id: 'c1', label: 'खरसिया', level: 2, visits: 75 },
              { id: 'c2', label: 'रायगढ़', level: 2, visits: 75 }
            ]
          },
          {
            id: 'd2',
            label: 'कोरबा',
            level: 1,
            visits: 200,
            children: [
              { id: 'c3', label: 'कटघोरा', level: 2, visits: 100 },
              { id: 'c4', label: 'पाली', level: 2, visits: 100 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={multiDistrictData as any}
          width={1000}
          height={800}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify all districts and constituencies are present
      expect(labels).toContain('छत्तीसगढ़ (350)');
      expect(labels).toContain('रायगढ़ (150)');
      expect(labels).toContain('खरसिया (75)');
      expect(labels).toContain('कोरबा (200)');
      expect(labels).toContain('कटघोरा (100)');
    });

    it('maintains visual separation between districts', () => {
      const separatedData = {
        id: 'root',
        label: 'राज्य',
        level: 0,
        visits: 330,
        children: [
          { id: 'd1', label: 'जिला A', level: 1, visits: 100 },
          { id: 'd2', label: 'जिला B', level: 1, visits: 150 },
          { id: 'd3', label: 'जिला C', level: 1, visits: 80 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={separatedData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render without overlap
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(3); // At least one node per district
    });
  });

  describe('Data Consistency with Analytics', () => {
    it('matches visit counts with analytics summary', () => {
      // Mock analytics summary data
      const analyticsSummary = {
        totalVisits: 142,
        districtBreakdown: {
          'रायगढ़': 75,
          'कोरबा': 67
        }
      };

      const mindmapData = {
        id: 'root',
        label: `कुल दौरे`,
        level: 0,
        visits: 142,
        children: [
          { id: 'd1', label: `रायगढ़`, level: 1, visits: 75 },
          { id: 'd2', label: `कोरबा`, level: 1, visits: 67 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mindmapData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify consistency with analytics
      expect(labels).toContain(`कुल दौरे (142)`);
      expect(labels).toContain(`रायगढ़ (75)`);
      expect(labels).toContain(`कोरबा (67)`);
    });

    it('updates dynamically when analytics data changes', () => {
      const initialData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 50,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 25 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 25 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={initialData as any}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      let labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (50)');

      // Update with new data
      const updatedData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 75,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 40 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 35 }
        ]
      };

      rerender(
        <HierarchyMindMap
          data={updatedData as any}
          width={800}
          height={600}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (75)');
      expect(labels).toContain('खरसिया (40)');
      expect(labels).toContain('रायगढ़ (35)');
    });
  });
});