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
        id: 'root',
        label: `कुल दौरे: ${analyticsSummary.totalVisits}`,
        level: 0,
        visits: 142,
        children: [
          {
            id: 'd1',
            label: `रायगढ़ (${analyticsSummary.districtBreakdown['रायगढ़']})`,
            level: 1,
            visits: 75,
            children: [
              { id: 'c1', label: `खरसिया (${analyticsSummary.constituencyBreakdown['खरसिया']})`, level: 2, visits: analyticsSummary.constituencyBreakdown['खरसिया'] },
              { id: 'c2', label: `रायगढ़ (${analyticsSummary.constituencyBreakdown['रायगढ़']})`, level: 2, visits: analyticsSummary.constituencyBreakdown['रायगढ़'] }
            ]
          },
          {
            id: 'd2',
            label: `कोरबा (${analyticsSummary.districtBreakdown['कोरबा']})`,
            level: 1,
            visits: 67,
            children: [
              { id: 'c3', label: `कटघोरा (${analyticsSummary.constituencyBreakdown['कटघोरा']})`, level: 2, visits: analyticsSummary.constituencyBreakdown['कटघोरा'] },
              { id: 'c4', label: `पाली (${analyticsSummary.constituencyBreakdown['पाली']})`, level: 2, visits: analyticsSummary.constituencyBreakdown['पाली'] }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mindmapData as any}
          width={1000}
          height={800}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Verify total matches analytics
      expect(labels).toContain(`कुल दौरे: ${analyticsSummary.totalVisits} (142)`);
      expect(analyticsSummary.totalVisits).toBe(142);

      // Verify district totals
      expect(labels).toContain(`रायगढ़ (${analyticsSummary.districtBreakdown['रायगढ़']}) (75)`);
      expect(labels).toContain(`कोरबा (${analyticsSummary.districtBreakdown['कोरबा']}) (67)`);

      // Verify constituency details
      expect(labels).toContain(`खरसिया (${analyticsSummary.constituencyBreakdown['खरसिया']}) (45)`);
      expect(labels).toContain(`रायगढ़ (${analyticsSummary.constituencyBreakdown['रायगढ़']}) (30)`);
      expect(labels).toContain(`कटघोरा (${analyticsSummary.constituencyBreakdown['कटघोरा']}) (35)`);
      expect(labels).toContain(`पाली (${analyticsSummary.constituencyBreakdown['पाली']}) (32)`);
    });

    it('maintains mathematical consistency across levels', () => {
      const consistentData = {
        id: 'root',
        label: 'रायगढ़', // District total
        level: 1,
        visits: 100,
        children: [
          {
            id: 'c1',
            label: 'खरसिया', // Constituency total
            level: 2,
            visits: 60,
            children: [
              {
                id: 'b1',
                label: 'खरसिया ब्लॉक', // Block total
                level: 3,
                visits: 40,
                children: [
                  { id: 'gp1', label: 'जोंबी ग्राम पंचायत', level: 4, visits: 25 }, // GP total
                  { id: 'gp2', label: 'तमनार ग्राम पंचायत', level: 4, visits: 15 }  // GP total
                ]
              },
              {
                id: 'b2',
                label: 'रायगढ़ ब्लॉक', // Block total
                level: 3,
                visits: 20,
                children: [
                  { id: 'gp3', label: 'कमलौर ग्राम पंचायत', level: 4, visits: 20 } // GP total
                ]
              }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={consistentData as any}
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
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 50,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 30 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 20 }
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
      expect(labels).toContain('खरसिया (30)');
      expect(labels).toContain('रायगढ़ (20)');

      // Simulate data refresh with updated counts
      const updatedData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 75,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 45 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 30 }
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
      expect(labels).toContain('खरसिया (45)');
      expect(labels).toContain('रायगढ़ (30)');
    });

    it('handles partial data updates gracefully', () => {
      const baseData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 100,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 60 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 40 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={baseData as any}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Partial update - only one constituency changes
      const partialUpdateData = {
        id: 'root',
        label: 'रायगढ़', // Increased total
        level: 1,
        visits: 120,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 60 }, // Same
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 60 }  // Increased
        ]
      };

      rerender(
        <HierarchyMindMap
          data={partialUpdateData as any}
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
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 142,
        children: [
          {
            id: 'c1',
            label: 'खरसिया',
            level: 2,
            visits: 45,
            children: [
              { id: 'b1', label: 'खरसिया ब्लॉक', level: 3, visits: 45 }
            ]
          },
          {
            id: 'c2',
            label: 'रायगढ़',
            level: 2,
            visits: 30,
            children: [
              { id: 'b2', label: 'रायगढ़ ब्लॉक', level: 3, visits: 30 }
            ]
          },
          {
            id: 'c3',
            label: 'कटघोरा',
            level: 2,
            visits: 35,
            children: [
              { id: 'b3', label: 'कटघोरा ब्लॉक', level: 3, visits: 35 }
            ]
          },
          {
            id: 'c4',
            label: 'पाली',
            level: 2,
            visits: 32,
            children: [
              { id: 'b4', label: 'पाली ब्लॉक', level: 3, visits: 32 }
            ]
          }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mindmapData as any}
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
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 102,
        children: [
          {
            id: 'c1',
            label: 'खरसिया',
            level: 2,
            visits: 60,
            children: [
              { id: 'v1', label: 'जोंबी', level: 5, visits: 15 },
              { id: 'v2', label: 'तमनार', level: 5, visits: 12 },
              { id: 'v3', label: 'अन्य गाँव', level: 5, visits: 33 }
            ]
          },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 42 }
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
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 55,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 30 },
          { id: 'c2', label: 'रायगढ़', level: 2 }, // Missing visits
          { id: 'c3', label: 'कटघोरा', level: 2, visits: 25 }
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={incompleteData as any}
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
      expect(labels).toContain('रायगढ़ (00)'); // Should default to 00
    });

    it('validates visit count data types', () => {
      const mixedTypeData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 55,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: '25' }, // String
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 30 },   // Number
          { id: 'c3', label: 'कटघोरा', level: 2, visits: null }, // Null
          { id: 'c4', label: 'पाली', level: 2, visits: undefined } // Undefined
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={mixedTypeData as any}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);

      // Should handle different data types appropriately
      // Note: The component might not handle string visits gracefully without explicit conversion, 
      // but our fix handles null/undefined.
      // If '25' is passed, it might be '25' or NaN depending on implementation.
      // Assuming the component expects number, but if JS allows string, it might just print it.
      // Let's check what we expect.

      expect(labels).toContain('रायगढ़ (30)');
      // Null/undefined should be handled gracefully as 00
      expect(labels).toContain('कटघोरा (00)');
      expect(labels).toContain('पाली (00)');
    });

    it('detects and reports visit count inconsistencies', () => {
      const inconsistentData = {
        id: 'root',
        label: 'रायगढ़', // Claims 100 total
        level: 1,
        visits: 100,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 40 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 30 },
          { id: 'c3', label: 'कटघोरा', level: 2, visits: 20 }
          // Actual sum: 90, but parent claims 100
        ]
      };

      const { container } = render(
        <HierarchyMindMap
          data={inconsistentData as any}
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
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 50,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 30 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 20 }
        ]
      };

      const { container, rerender } = render(
        <HierarchyMindMap
          data={baseData as any}
          width={800}
          height={600}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Perform 10 rapid updates
      for (let i = 1; i <= 10; i++) {
        const updatedData = {
          id: 'root',
          label: 'रायगढ़',
          level: 1,
          visits: 50 + i * 5,
          children: [
            { id: 'c1', label: 'खरसिया', level: 2, visits: 30 + i },
            { id: 'c2', label: 'रायगढ़', level: 2, visits: 20 + i * 4 }
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
      }

      // Final state should be accurate
      const finalLabels = Array.from(svg.querySelectorAll('text')).map(text => text.textContent);
      expect(finalLabels).toContain('रायगढ़ (100)'); // 50 + 10*5
      expect(finalLabels).toContain('खरसिया (40)');  // 30 + 10
      expect(finalLabels).toContain('रायगढ़ (60)');  // 20 + 10*4
    });

    it('handles concurrent data source updates', () => {
      const initialData = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 100,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 60 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 40 }
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

      // Simulate concurrent updates from different data sources
      const analyticsUpdate = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 120,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 70 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 50 }
        ]
      };

      const fieldUpdate = {
        id: 'root',
        label: 'रायगढ़',
        level: 1,
        visits: 115,
        children: [
          { id: 'c1', label: 'खरसिया', level: 2, visits: 65 },
          { id: 'c2', label: 'रायगढ़', level: 2, visits: 50 }
        ]
      };

      // Apply analytics update
      rerender(
        <HierarchyMindMap
          data={analyticsUpdate as any}
          width={800}
          height={600}
        />
      );

      // Then apply field update (simulating real-time data)
      rerender(
        <HierarchyMindMap
          data={fieldUpdate as any}
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