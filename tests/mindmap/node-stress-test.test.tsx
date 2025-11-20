import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';

describe('D3 HierarchyMindMap - Node Stress Test', () => {
  describe('Large Hierarchy Performance', () => {
    it('renders 500 nodes within acceptable time', () => {
      // Generate large synthetic hierarchy
      const generateLargeHierarchy = (districts: number, maxDepth: number = 4) => {
        const districtsData = [];

        for (let d = 1; d <= districts; d++) {
          const district = {
            name: `जिला ${d}`,
            children: []
          };

          // Add constituencies (2-3 per district)
          const constituencies = Math.floor(Math.random() * 2) + 2;
          for (let c = 1; c <= constituencies; c++) {
            const constituency = {
              name: `विधानसभा ${d}-${c}`,
              children: []
            };

            // Add blocks (1-2 per constituency)
            const blocks = Math.floor(Math.random() * 2) + 1;
            for (let b = 1; b <= blocks; b++) {
              const block = {
                name: `विकासखंड ${d}-${c}-${b}`,
                children: []
              };

              // Add GPs (2-4 per block)
              const gps = Math.floor(Math.random() * 3) + 2;
              for (let g = 1; g <= gps; g++) {
                const gp = {
                  name: `ग्राम पंचायत ${d}-${c}-${b}-${g}`,
                  children: []
                };

                // Add villages (1-3 per GP)
                const villages = Math.floor(Math.random() * 3) + 1;
                for (let v = 1; v <= villages; v++) {
                  gp.children.push({
                    name: `गाँव ${d}-${c}-${b}-${g}-${v}`,
                    visits: Math.floor(Math.random() * 50) + 1
                  });
                }

                block.children.push(gp);
              }

              constituency.children.push(block);
            }

            district.children.push(constituency);
          }

          districtsData.push(district);
        }

        return {
          name: 'छत्तीसगढ़ राज्य',
          children: districtsData
        };
      };

      const largeData = generateLargeHierarchy(10); // 10 districts = ~500+ nodes

      const startTime = performance.now();

      const { container } = render(
        <HierarchyMindMap
          data={largeData}
          width={2000}
          height={1500}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render within 5 seconds
      expect(renderTime).toBeLessThan(5000);

      // Should have rendered all nodes
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(100);
    });

    it('handles 1000+ nodes without UI freeze', () => {
      // Create ultra-large hierarchy
      const createUltraLargeHierarchy = () => {
        const villages = [];
        for (let i = 1; i <= 1000; i++) {
          villages.push({
            name: `गाँव ${i}`,
            visits: Math.floor(Math.random() * 20) + 1
          });
        }

        return {
          name: 'बड़ा ज़िला',
          children: [
            {
              name: 'विकासखंड A',
              children: villages.slice(0, 333).map(v => ({ ...v }))
            },
            {
              name: 'विकासखंड B',
              children: villages.slice(333, 666).map(v => ({ ...v }))
            },
            {
              name: 'विकासखंड C',
              children: villages.slice(666).map(v => ({ ...v }))
            }
          ]
        };
      };

      const ultraLargeData = createUltraLargeHierarchy();

      const startTime = performance.now();

      const { container } = render(
        <HierarchyMindMap
          data={ultraLargeData}
          width={2500}
          height={2000}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render within 10 seconds (allowing for large dataset)
      expect(renderTime).toBeLessThan(10000);

      // Should have rendered many nodes
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(500);
    });
  });

  describe('Interactive Performance with Large Datasets', () => {
    it('maintains hover responsiveness on 200+ nodes', async () => {
      // Create medium-large hierarchy
      const createMediumHierarchy = () => {
        const data = { name: 'ज़िला', children: [] };

        for (let i = 1; i <= 20; i++) {
          const block = {
            name: `विकासखंड ${i}`,
            children: []
          };

          for (let j = 1; j <= 10; j++) {
            block.children.push({
              name: `गाँव ${i}-${j}`,
              visits: Math.floor(Math.random() * 30) + 1
            });
          }

          data.children.push(block);
        }

        return data;
      };

      const mediumData = createMediumHierarchy();

      const { container } = render(
        <HierarchyMindMap
          data={mediumData}
          width={1500}
          height={1200}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Test hover performance on multiple nodes
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(50);

      // Simulate hover events
      const hoverStartTime = performance.now();

      nodes.forEach((node, index) => {
        if (index < 10) { // Test first 10 nodes
          node.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
          node.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true }));
        }
      });

      const hoverEndTime = performance.now();
      const hoverTime = hoverEndTime - hoverStartTime;

      // Hover interactions should be fast
      expect(hoverTime).toBeLessThan(1000);
    });

    it('handles zoom/pan operations on dense hierarchies', () => {
      const createDenseHierarchy = () => {
        const data = { name: 'घना ज़िला', children: [] };

        for (let i = 1; i <= 15; i++) {
          const constituency = {
            name: `विधानसभा ${i}`,
            children: []
          };

          for (let j = 1; j <= 8; j++) {
            const block = {
              name: `विकासखंड ${i}-${j}`,
              children: []
            };

            for (let k = 1; k <= 5; k++) {
              block.children.push({
                name: `गाँव ${i}-${j}-${k}`,
                visits: Math.floor(Math.random() * 25) + 1
              });
            }

            constituency.children.push(block);
          }

          data.children.push(constituency);
        }

        return data;
      };

      const denseData = createDenseHierarchy();

      const { container } = render(
        <HierarchyMindMap
          data={denseData}
          width={1800}
          height={1400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render dense hierarchy
      const nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(200);

      // Simulate zoom and pan operations
      const zoomPanStartTime = performance.now();

      // Mock zoom event
      svg.dispatchEvent(new WheelEvent('wheel', { deltaY: -100 }));

      // Mock pan events
      svg.dispatchEvent(new MouseEvent('mousedown', { clientX: 100, clientY: 100 }));
      svg.dispatchEvent(new MouseEvent('mousemove', { clientX: 150, clientY: 150 }));
      svg.dispatchEvent(new MouseEvent('mouseup'));

      const zoomPanEndTime = performance.now();
      const zoomPanTime = zoomPanEndTime - zoomPanStartTime;

      // Zoom/pan should be responsive
      expect(zoomPanTime).toBeLessThan(500);
    });
  });

  describe('Memory Usage with Large Hierarchies', () => {
    it('manages memory efficiently with 500+ nodes', () => {
      // This test would typically use performance.memory in browser
      // For Node.js testing, we'll simulate memory monitoring

      const createMemoryIntensiveHierarchy = () => {
        const data = { name: 'मेमोरी टेस्ट ज़िला', children: [] };

        for (let i = 1; i <= 25; i++) {
          const block = {
            name: `विकासखंड ${i}`,
            children: []
          };

          for (let j = 1; j <= 20; j++) {
            block.children.push({
              name: `गाँव ${i}-${j}`,
              visits: j,
              // Add extra properties to increase memory usage
              metadata: {
                population: Math.floor(Math.random() * 10000),
                area: Math.random() * 100,
                coordinates: [Math.random() * 180 - 90, Math.random() * 360 - 180],
                facilities: ['school', 'hospital', 'market']
              }
            });
          }

          data.children.push(block);
        }

        return data;
      };

      const memoryData = createMemoryIntensiveHierarchy();

      const beforeMemory = process.memoryUsage?.()?.heapUsed || 0;

      const { container } = render(
        <HierarchyMindMap
          data={memoryData}
          width={1600}
          height={1200}
        />
      );

      const afterMemory = process.memoryUsage?.()?.heapUsed || 0;
      const memoryDelta = afterMemory - beforeMemory;

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Memory usage should be reasonable (< 50MB increase)
      expect(memoryDelta).toBeLessThan(50 * 1024 * 1024);
    });

    it('cleans up resources after unmounting large hierarchies', () => {
      const createLargeHierarchy = () => {
        const data = { name: 'क्लीनअप टेस्ट', children: [] };

        for (let i = 1; i <= 30; i++) {
          const block = { name: `ब्लॉक ${i}`, children: [] };
          for (let j = 1; j <= 15; j++) {
            block.children.push({ name: `गाँव ${i}-${j}`, visits: j });
          }
          data.children.push(block);
        }

        return data;
      };

      const cleanupData = createLargeHierarchy();

      const { container, unmount } = render(
        <HierarchyMindMap
          data={cleanupData}
          width={1400}
          height={1000}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Verify nodes exist
      let nodes = svg.querySelectorAll('circle, rect');
      expect(nodes.length).toBeGreaterThan(100);

      // Unmount component
      unmount();

      // Container should be empty
      expect(container.firstChild).toBeNull();
    });
  });

  describe('Rendering Performance Benchmarks', () => {
    it('maintains consistent render times across different sizes', () => {
      const sizes = [
        { width: 600, height: 400, expectedNodes: 50 },
        { width: 1000, height: 700, expectedNodes: 150 },
        { width: 1600, height: 1200, expectedNodes: 300 },
      ];

      const createScaledHierarchy = (targetNodes: number) => {
        const data = { name: 'स्केल टेस्ट', children: [] };
        const nodesPerLevel = Math.ceil(Math.sqrt(targetNodes / 3));

        for (let i = 1; i <= nodesPerLevel; i++) {
          const block = { name: `ब्लॉक ${i}`, children: [] };
          for (let j = 1; j <= nodesPerLevel; j++) {
            block.children.push({ name: `गाँव ${i}-${j}`, visits: (i + j) % 20 + 1 });
          }
          data.children.push(block);
        }

        return data;
      };

      const renderTimes: number[] = [];

      sizes.forEach(({ width, height, expectedNodes }) => {
        const testData = createScaledHierarchy(expectedNodes);
        const startTime = performance.now();

        const { container } = render(
          <HierarchyMindMap
            data={testData}
            width={width}
            height={height}
          />
        );

        const endTime = performance.now();
        renderTimes.push(endTime - startTime);

        const svg = container.querySelector('svg');
        expect(svg).toBeInTheDocument();
      });

      // Render times should scale reasonably with size
      expect(renderTimes[0]).toBeLessThan(renderTimes[1]);
      expect(renderTimes[1]).toBeLessThan(renderTimes[2]);

      // Largest size should still render within 3 seconds
      expect(renderTimes[2]).toBeLessThan(3000);
    });

    it('handles rapid data updates without degradation', () => {
      const baseData = {
        name: 'रिपिड अपडेट टेस्ट',
        children: [
          { name: 'नोड 1', visits: 10 },
          { name: 'नोड 2', visits: 20 },
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

      const updateTimes: number[] = [];

      // Perform 20 rapid updates
      for (let i = 1; i <= 20; i++) {
        const updatedData = {
          ...baseData,
          children: baseData.children.map(child => ({
            ...child,
            visits: child.visits + i
          }))
        };

        const updateStartTime = performance.now();

        rerender(
          <HierarchyMindMap
            data={updatedData}
            width={800}
            height={600}
          />
        );

        const updateEndTime = performance.now();
        updateTimes.push(updateEndTime - updateStartTime);

        svg = container.querySelector('svg');
        expect(svg).toBeInTheDocument();
      }

      // Average update time should remain low
      const avgUpdateTime = updateTimes.reduce((a, b) => a + b, 0) / updateTimes.length;
      expect(avgUpdateTime).toBeLessThan(100); // Less than 100ms per update

      // Updates should not get progressively slower
      const firstHalfAvg = updateTimes.slice(0, 10).reduce((a, b) => a + b, 0) / 10;
      const secondHalfAvg = updateTimes.slice(10).reduce((a, b) => a + b, 0) / 10;
      expect(secondHalfAvg).toBeLessThan(firstHalfAvg * 1.5); // No more than 50% degradation
    });
  });
});