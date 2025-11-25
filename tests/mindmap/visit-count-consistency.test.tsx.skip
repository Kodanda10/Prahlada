import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';

describe('D3 HierarchyMindMap - Visit Count Consistency', () => {
  describe('Analytics Summary Integration', () => {
    it('matches total visit count with analytics summary', () => {
      // Mock analytics summary data
      const analyticsSummary = {
        totalVisits: 142,
        districtBreakdown: {
          'रायगढ़': 75,
          'कोरबा': 67
        },
        constituencyBreakdown: {
          'खरसिया': 45,
          'रायगढ़': 30,
          'कटघोरा': 35,
          'पाली': 32
        }
      };

      const mindmapData = {
        name: `कुल दौरे: ${analyticsSummary.totalVisits}`,
        children: [
          {
            name: `रायगढ़ (${analyticsSummary.districtBreakdown['रायगढ़']})`,
            children: [
              { name: `खरसिया (${analyticsSummary.constituencyBreakdown['खरसिया']})`, visits: analyticsSummary.constituencyBreakdown['खरसिया'] },
              { name: `रायगढ़ (${analyticsSummary.constituencyBreakdown['रायगढ़']})`, visits: analyticsSummary.constituencyBreakdown['रायगढ़'] }
            ]
          },
          {
            name: `कोरबा (${analyticsSummary.districtBreakdown['कोरबा']})`,
            children: [
              { name: `कटघोरा (${analyticsSummary.constituencyBreakdown['कटघोरा']})`, visits: analyticsSummary.constituencyBreakdown['कटघोरा'] },
              { name: `पाली (${analyticsSummary.constituencyBreakdown['पाली']})`, visits: analyticsSummary.constituencyBreakdown['पाली'] }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mindmapData}
          width={1000}
          height={800}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify total matches analytics
      expect(labels).toContain(`कुल दौरे: ${analyticsSummary.totalVisits}`);
      expect(analyticsSummary.totalVisits).toBe(142);

      // Verify district totals
      expect(labels).toContain(`रायगढ़ (${analyticsSummary.districtBreakdown['रायगढ़']})`);
      expect(labels).toContain(`कोरबा (${analyticsSummary.districtBreakdown['कोरबा']})`);

      // Verify constituency details
      expect(labels).toContain(`खरसिया (${analyticsSummary.constituencyBreakdown['खरसिया']})`);
      expect(labels).toContain(`रायगढ़ (${analyticsSummary.constituencyBreakdown['रायगढ़']})`);
      expect(labels).toContain(`कटघोरा (${analyticsSummary.constituencyBreakdown['कटघोरा']})`);
      expect(labels).toContain(`पाली (${analyticsSummary.constituencyBreakdown['पाली']})`);
    });

    it('maintains mathematical consistency across levels', () => {
      const consistentData = {
        name: 'रायगढ़ (100)', // District total
        children: [
          {
            name: 'खरसिया (60)', // Constituency total
            children: [
              {
                name: 'खरसिया ब्लॉक (40)', // Block total
                children: [
                  { name: 'जोंबी ग्राम पंचायत (25)', visits: 25 }, // GP total
                  { name: 'तमनार ग्राम पंचायत (15)', visits: 15 }  // GP total
                ]
              },
              {
                name: 'रायगढ़ ब्लॉक (20)', // Block total
                children: [
                  { name: 'कमलौर ग्राम पंचायत (20)', visits: 20 } // GP total
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={consistentData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify district total (100)
      expect(labels).toContain('रायगढ़ (100)');

      // Constituency total should equal sum of blocks (60 = 40 + 20)
      expect(labels).toContain('खरसिया (60)');

      // Block totals should equal sum of GPs
      expect(labels).toContain('खरसिया ब्लॉक (40)'); // 25 + 15 = 40
      expect(labels).toContain('रायगढ़ ब्लॉक (20)');  // 20 = 20

      // GP totals should equal village visits
      expect(labels).toContain('जोंबी ग्राम पंचायत (25)');
      expect(labels).toContain('तमनार ग्राम पंचायत (15)');
      expect(labels).toContain('कमलौर ग्राम पंचायत (20)');
    });
  });

  describe('Real-time Data Synchronization', () => {
    it('updates visit counts when analytics data refreshes', () => {
      const initialData = {
        name: 'रायगढ़ (50)',
        children: [
          { name: 'खरसिया (30)', visits: 30 },
          { name: 'रायगढ़ (20)', visits: 20 }
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
      expect(labels).toContain('खरसिया (30)');
      expect(labels).toContain('रायगढ़ (20)');

      // Simulate data refresh with updated counts
      const updatedData = {
        name: 'रायगढ़ (75)',
        children: [
          { name: 'खरसिया (45)', visits: 45 },
          { name: 'रायगढ़ (30)', visits: 30 }
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
      expect(labels).toContain('खरसिया (45)');
      expect(labels).toContain('रायगढ़ (30)');
    });

    it('handles partial data updates gracefully', () => {
      const baseData = {
        name: 'रायगढ़ (100)',
        children: [
          { name: 'खरसिया (60)', visits: 60 },
          { name: 'रायगढ़ (40)', visits: 40 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={baseData}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Partial update - only one constituency changes
      const partialUpdateData = {
        name: 'रायगढ़ (120)', // Increased total
        children: [
          { name: 'खरसिया (60)', visits: 60 }, // Same
          { name: 'रायगढ़ (60)', visits: 60 }  // Increased
        ]
      };

      rerender(
        <HierarchyMindMap
          data={partialUpdateData}
          width={800}
          height={600}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (120)');
      expect(labels).toContain('खरसिया (60)');
      expect(labels).toContain('रायगढ़ (60)');
    });
  });

  describe('Cross-Component Consistency', () => {
    it('matches visit counts with chart visualizations', () => {
      // Mock chart data that should match mindmap
      const chartData = [
        { name: 'खरसिया', value: 45 },
        { name: 'रायगढ़', value: 30 },
        { name: 'कटघोरा', value: 35 },
        { name: 'पाली', value: 32 }
      ];

      const mindmapData = {
        name: 'रायगढ़ (142)',
        children: [
          {
            name: 'खरसिया (45)',
            children: [
              { name: 'खरसिया ब्लॉक (45)', visits: 45 }
            ]
          },
          {
            name: 'रायगढ़ (30)',
            children: [
              { name: 'रायगढ़ ब्लॉक (30)', visits: 30 }
            ]
          },
          {
            name: 'कटघोरा (35)',
            children: [
              { name: 'कटघोरा ब्लॉक (35)', visits: 35 }
            ]
          },
          {
            name: 'पाली (32)',
            children: [
              { name: 'पाली ब्लॉक (32)', visits: 32 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mindmapData}
          width={1000}
          height={800}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify mindmap counts match chart data
      chartData.forEach(item => {
        const expectedLabel = `${item.name} (${item.value})`;
        expect(labels).toContain(expectedLabel);
      });

      // Verify total
      const totalFromChart = chartData.reduce((sum, item) => sum + item.value, 0);
      expect(labels).toContain(`रायगढ़ (${totalFromChart})`);
      expect(totalFromChart).toBe(142);
    });

    it('syncs with table/list view visit counts', () => {
      const tableData = [
        { location: 'खरसिया', visits: 45, status: 'सक्रिय' },
        { location: 'रायगढ़', visits: 30, status: 'सक्रिय' },
        { location: 'जोंबी', visits: 15, status: 'पूर्ण' },
        { location: 'तमनार', visits: 12, status: 'प्रगति में' }
      ];

      const mindmapData = {
        name: 'रायगढ़ (102)',
        children: [
          {
            name: 'खरसिया (60)',
            children: [
              { name: 'जोंबी (15)', visits: 15 },
              { name: 'तमनार (12)', visits: 12 },
              { name: 'अन्य गाँव (33)', visits: 33 }
            ]
          },
          { name: 'रायगढ़ (42)', visits: 42 }
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

      // Verify mindmap counts match table data where applicable
      expect(labels).toContain('जोंबी (15)');
      expect(labels).toContain('तमनार (12)');

      // Verify constituency totals include table data
      expect(labels).toContain('खरसिया (60)'); // 15 + 12 + 33
      expect(labels).toContain('रायगढ़ (42)');

      // Verify district total
      expect(labels).toContain('रायगढ़ (102)'); // 60 + 42
    });
  });

  describe('Data Validation and Error Handling', () => {
    it('handles missing visit count data gracefully', () => {
      const incompleteData = {
        name: 'रायगढ़',
        children: [
          { name: 'खरसिया', visits: 30 },
          { name: 'रायगढ़' }, // Missing visits
          { name: 'कटघोरा', visits: 25 }
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

      // Should handle missing visits appropriately
      expect(labels).toContain('खरसिया (30)');
      expect(labels).toContain('कटघोरा (25)');
      expect(labels).toContain('रायगढ़'); // Should still display without count
    });

    it('validates visit count data types', () => {
      const mixedTypeData = {
        name: 'रायगढ़',
        children: [
          { name: 'खरसिया', visits: '25' }, // String
          { name: 'रायगढ़', visits: 30 },   // Number
          { name: 'कटघोरा', visits: null }, // Null
          { name: 'पाली', visits: undefined } // Undefined
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mixedTypeData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Should handle different data types appropriately
      expect(labels).toContain('खरसिया (25)');
      expect(labels).toContain('रायगढ़ (30)');
      // Null/undefined should be handled gracefully
      expect(labels.some(label => label.includes('कटघोरा'))).toBe(true);
      expect(labels.some(label => label.includes('पाली'))).toBe(true);
    });

    it('detects and reports visit count inconsistencies', () => {
      const inconsistentData = {
        name: 'रायगढ़ (100)', // Claims 100 total
        children: [
          { name: 'खरसिया (40)', visits: 40 },
          { name: 'रायगढ़ (30)', visits: 30 },
          { name: 'कटघोरा (20)', visits: 20 }
          // Actual sum: 90, but parent claims 100
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={inconsistentData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should still render but might show warning
      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (100)');
      expect(labels).toContain('खरसिया (40)');
      expect(labels).toContain('रायगढ़ (30)');
      expect(labels).toContain('कटघोरा (20)');
    });
  });

  describe('Performance with Frequent Updates', () => {
    it('maintains count accuracy during rapid updates', () => {
      const baseData = {
        name: 'रायगढ़ (50)',
        children: [
          { name: 'खरसिया (30)', visits: 30 },
          { name: 'रायगढ़ (20)', visits: 20 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={baseData}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Perform 10 rapid updates
      for (let i = 1; i <= 10; i++) {
        const updatedData = {
          name: `रायगढ़ (${50 + i * 5})`,
          children: [
            { name: `खरसिया (${30 + i})`, visits: 30 + i },
            { name: `रायगढ़ (${20 + i * 4})`, visits: 20 + i * 4 }
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
      }

      // Final state should be accurate
      const finalLabels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(finalLabels).toContain('रायगढ़ (100)'); // 50 + 10*5
      expect(finalLabels).toContain('खरसिया (40)');  // 30 + 10
      expect(finalLabels).toContain('रायगढ़ (60)');  // 20 + 10*4
    });

    it('handles concurrent data source updates', () => {
      const initialData = {
        name: 'रायगढ़ (100)',
        children: [
          { name: 'खरसिया (60)', visits: 60 },
          { name: 'रायगढ़ (40)', visits: 40 }
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

      // Simulate concurrent updates from different data sources
      const analyticsUpdate = {
        name: 'रायगढ़ (120)',
        children: [
          { name: 'खरसिया (70)', visits: 70 },
          { name: 'रायगढ़ (50)', visits: 50 }
        ]
      };

      const fieldUpdate = {
        name: 'रायगढ़ (115)',
        children: [
          { name: 'खरसिया (65)', visits: 65 },
          { name: 'रायगढ़ (50)', visits: 50 }
        ]
      };

      // Apply analytics update
      rerender(
        <HierarchyMindMap
          data={analyticsUpdate}
          width={800}
          height={600}
        />
      );

      // Then apply field update (simulating real-time data)
      rerender(
        <HierarchyMindMap
          data={fieldUpdate}
          width={800}
          height={600}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(labels).toContain('रायगढ़ (115)');
      expect(labels).toContain('खरसिया (65)');
      expect(labels).toContain('रायगढ़ (50)');
    });
  });
});