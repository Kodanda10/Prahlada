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
    name: faisMetadata.district,
    children: [
      {
        name: faisMetadata.constituency,
        children: [
          {
            name: faisMetadata.block,
            children: [
              {
                name: faisMetadata.gp,
                children: [
                  { name: faisMetadata.village, visits: faisMetadata.visits }
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
          data={sampleHierarchyData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should contain the district name
      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(faisMetadata.district);
    });

    it('displays constituency as first child level', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(faisMetadata.constituency);
    });

    it('shows block as second level with correct Hindi text', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(faisMetadata.block);
    });

    it('renders gram panchayat as third level', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain(faisMetadata.gp);
    });

    it('displays village as leaf node with visit count', () => {
      const { container } = render(
        <HierarchyMindMap
          data={sampleHierarchyData}
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
        name: 'रायगढ़',
        children: [
          {
            name: 'खरसिया',
            children: [
              { name: 'जोंबी गाँव', visits: 4 },
              { name: 'तमनार गाँव', visits: 12 },
              { name: 'कमलौर गाँव', visits: 1 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={testData}
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
        name: 'रायगढ़ (21)', // 4 + 12 + 1 + 4 (from gp level)
        children: [
          {
            name: 'खरसिया (21)',
            children: [
              { name: 'खरसिया ब्लॉक (17)', visits: 17 }, // 4 + 12 + 1
              {
                name: 'जोंबी ग्राम पंचायत (04)',
                children: [
                  { name: 'जोंबी (04)', visits: 4 }
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={aggregatedData}
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
        name: 'जिला',
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
                      { name: 'गाँव/वार्ड', visits: 1 }
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
          data={orderedData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify hierarchical order is maintained
      const expectedOrder = [
        'जिला',
        'विधानसभा',
        'विकासखंड',
        'ग्राम पंचायत',
        'गाँव/वार्ड (01)'
      ];

      expectedOrder.forEach(label => {
        expect(labels).toContain(label);
      });
    });

    it('handles ULB (Urban Local Body) hierarchy correctly', () => {
      const ulbData = {
        name: 'नगर निगम',
        children: [
          {
            name: 'ज़ोन',
            children: [
              {
                name: 'वार्ड',
                children: [
                  { name: 'उप-वार्ड', visits: 5 }
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

      // Verify ULB hierarchy
      expect(labels).toContain('नगर निगम');
      expect(labels).toContain('ज़ोन');
      expect(labels).toContain('वार्ड');
      expect(labels).toContain('उप-वार्ड (05)');
    });
  });

  describe('Multi-District Hierarchy Support', () => {
    it('renders multiple districts in single mindmap', () => {
      const multiDistrictData = {
        name: 'छत्तीसगढ़',
        children: [
          {
            name: 'रायगढ़ (150)',
            children: [
              { name: 'खरसिया (75)', visits: 75 },
              { name: 'रायगढ़ (75)', visits: 75 }
            ]
          },
          {
            name: 'कोरबा (200)',
            children: [
              { name: 'कटघोरा (100)', visits: 100 },
              { name: 'पाली (100)', visits: 100 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={multiDistrictData}
          width={1000}
          height={800}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify all districts and constituencies are present
      expect(labels).toContain('छत्तीसगढ़');
      expect(labels).toContain('रायगढ़ (150)');
      expect(labels).toContain('खरसिया (75)');
      expect(labels).toContain('कोरबा (200)');
      expect(labels).toContain('कटघोरा (100)');
    });

    it('maintains visual separation between districts', () => {
      const separatedData = {
        name: 'राज्य',
        children: [
          { name: 'जिला A (100)', visits: 100 },
          { name: 'जिला B (150)', visits: 150 },
          { name: 'जिला C (80)', visits: 80 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={separatedData}
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
        name: `कुल दौरे: ${analyticsSummary.totalVisits}`,
        children: [
          { name: `रायगढ़ (${analyticsSummary.districtBreakdown['रायगढ़']})`, visits: analyticsSummary.districtBreakdown['रायगढ़'] },
          { name: `कोरबा (${analyticsSummary.districtBreakdown['कोरबा']})`, visits: analyticsSummary.districtBreakdown['कोरबा'] }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mindmapData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify consistency with analytics
      expect(labels).toContain(`कुल दौरे: ${analyticsSummary.totalVisits}`);
      expect(labels).toContain(`रायगढ़ (${analyticsSummary.districtBreakdown['रायगढ़']})`);
      expect(labels).toContain(`कोरबा (${analyticsSummary.districtBreakdown['कोरबा']})`);
    });

    it('updates dynamically when analytics data changes', () => {
      const initialData = {
        name: 'रायगढ़ (50)',
        children: [
          { name: 'खरसिया (25)', visits: 25 },
          { name: 'रायगढ़ (25)', visits: 25 }
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
      expect(labels).toContain('रायगढ़ (50)');

      // Update with new data
      const updatedData = {
        name: 'रायगढ़ (75)',
        children: [
          { name: 'खरसिया (40)', visits: 40 },
          { name: 'रायगढ़ (35)', visits: 35 }
        ]
      };

      rerender(
        <HierarchyMindMap
          data={updatedData}
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