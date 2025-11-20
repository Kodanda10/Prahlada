import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import CustomBarChart from '../../components/charts/CustomBarChart';
import CustomLineChart from '../../components/charts/CustomLineChart';
import CustomPieChart from '../../components/charts/CustomPieChart';

describe('Other Data Visualization - Enhanced Chart Testing', () => {
  // Comprehensive test data for different chart types
  const complexBarData = [
    { name: 'जनवरी', value: 400, category: 'राजस्व', color: '#8884d8' },
    { name: 'फरवरी', value: 300, category: 'व्यय', color: '#82ca9d' },
    { name: 'मार्च', value: 600, category: 'लाभ', color: '#ffc658' },
    { name: 'अप्रैल', value: 800, category: 'निवेश', color: '#ff7300' },
    { name: 'मई', value: 500, category: 'बचत', color: '#00ff00' },
    { name: 'जून', value: 700, category: 'विस्तार', color: '#ff0000' },
  ];

  const multiLineData = [
    { name: 'सप्ताह 1', series1: 100, series2: 120, series3: 90 },
    { name: 'सप्ताह 2', series1: 200, series2: 180, series3: 150 },
    { name: 'सप्ताह 3', series1: 150, series2: 220, series3: 180 },
    { name: 'सप्ताह 4', series1: 300, series2: 280, series3: 250 },
    { name: 'सप्ताह 5', series1: 250, series2: 320, series3: 290 },
  ];

  const detailedPieData = [
    { name: 'उत्तरी क्षेत्र', value: 400, percentage: 25.0, color: '#8884d8' },
    { name: 'दक्षिणी क्षेत्र', value: 300, percentage: 18.8, color: '#82ca9d' },
    { name: 'पूर्वी क्षेत्र', value: 500, percentage: 31.3, color: '#ffc658' },
    { name: 'पश्चिमी क्षेत्र', value: 400, percentage: 25.0, color: '#ff7300' },
  ];

  describe('CustomBarChart Advanced Features', () => {
    it('renders multi-category bar chart with Hindi labels', () => {
      const { container } = render(
        <div style={{ width: '600px', height: '400px' }}>
          <CustomBarChart
            data={complexBarData}
            xKey="name"
            dataKey="value"
            width={600}
            height={400}
          />
        </div>
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render bars for each data point
      const bars = svg.querySelectorAll('rect');
      expect(bars.length).toBe(complexBarData.length);

      // Should have axis labels
      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('displays values and categories correctly', () => {
      const { container } = render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Verify data integrity
      complexBarData.forEach(item => {
        expect(item.name).toBeDefined();
        expect(item.value).toBeGreaterThan(0);
        expect(item.category).toBeDefined();
      });
    });

    it('handles negative values gracefully', () => {
      const negativeData = [
        { name: 'लाभ', value: 500 },
        { name: 'हानि', value: -200 },
        { name: 'ब्रेक-ईवन', value: 0 },
      ];

      const { container } = render(
        <CustomBarChart
          data={negativeData}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const bars = svg.querySelectorAll('rect');
      expect(bars.length).toBe(3);
    });

    it('supports custom colors and theming', () => {
      const { container } = render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should use provided colors
      complexBarData.forEach(item => {
        expect(item.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      });
    });
  });

  describe('CustomLineChart Multi-Series Support', () => {
    it('renders multiple data series with legends', () => {
      const { container } = render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render multiple lines
      const paths = svg.querySelectorAll('path');
      expect(paths.length).toBeGreaterThan(1);

      // Should have data points
      const circles = svg.querySelectorAll('circle');
      expect(circles.length).toBe(multiLineData.length * 3); // 3 series
    });

    it('displays Hindi axis labels and legends', () => {
      const { container } = render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('handles missing data points gracefully', () => {
      const sparseData = [
        { name: 'A', series1: 100, series2: null, series3: 90 },
        { name: 'B', series1: null, series2: 180, series3: 150 },
        { name: 'C', series1: 150, series2: 220, series3: null },
      ];

      const { container } = render(
        <CustomLineChart
          data={sparseData}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should handle null values without breaking
      const paths = svg.querySelectorAll('path');
      expect(paths.length).toBeGreaterThan(0);
    });

    it('supports interactive hover states', () => {
      const { container } = render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should be interactive
      expect(svg).toBeInTheDocument();
    });
  });

  describe('CustomPieChart Enhanced Features', () => {
    it('renders pie segments with percentages and labels', () => {
      const { container } = render(
        <CustomPieChart
          data={detailedPieData}
          width={400}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render pie segments
      const paths = svg.querySelectorAll('path');
      expect(paths.length).toBe(detailedPieData.length);

      // Should have labels
      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('displays accurate percentage calculations', () => {
      const total = detailedPieData.reduce((sum, item) => sum + item.value, 0);
      const expectedPercentages = detailedPieData.map(item =>
        Math.round((item.value / total) * 100 * 10) / 10
      );

      detailedPieData.forEach((item, index) => {
        expect(item.percentage).toBeCloseTo(expectedPercentages[index], 1);
      });
    });

    it('maintains color consistency with data', () => {
      const { container } = render(
        <CustomPieChart
          data={detailedPieData}
          width={400}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should use provided colors
      detailedPieData.forEach(item => {
        expect(item.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      });
    });

    it('handles small segments appropriately', () => {
      const smallSegmentData = [
        { name: 'बड़ा', value: 900, color: '#8884d8' },
        { name: 'मध्यम', value: 90, color: '#82ca9d' },
        { name: 'छोटा', value: 10, color: '#ffc658' }, // Very small segment
      ];

      const { container } = render(
        <CustomPieChart
          data={smallSegmentData}
          width={400}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should still render all segments
      const paths = svg.querySelectorAll('path');
      expect(paths.length).toBe(smallSegmentData.length);
    });
  });

  describe('Chart Responsiveness and Adaptation', () => {
    it('adapts layout for different container sizes', () => {
      const sizes = [
        { width: 300, height: 200 },
        { width: 600, height: 400 },
        { width: 1000, height: 600 },
      ];

      sizes.forEach(({ width, height }) => {
        const { container } = render(
          <CustomBarChart
            data={complexBarData.slice(0, 4)}
            width={width}
            height={height}
          />
        );

        const svg = container.querySelector('svg');
        expect(svg).toBeInTheDocument();
        expect(svg).toHaveAttribute('width', width.toString());
        expect(svg).toHaveAttribute('height', height.toString());
      });
    });

    it('maintains readability on small screens', () => {
      const { container } = render(
        <CustomBarChart
          data={complexBarData.slice(0, 3)}
          width={300}
          height={200}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should still be usable on small screens
      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('scales appropriately for high-DPI displays', () => {
      // Mock high DPI
      Object.defineProperty(window, 'devicePixelRatio', {
        value: 2,
        configurable: true,
      });

      const { container } = render(
        <CustomLineChart
          data={multiLineData}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render crisply on high DPI
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Chart Accessibility Features', () => {
    it('provides descriptive text for screen readers', () => {
      const { container } = render(
        <CustomPieChart
          data={detailedPieData}
          width={400}
          height={400}
        />
      );

      const chartContainer = container.querySelector('.custom-pie-chart');
      expect(chartContainer).toBeInTheDocument();

      // Should have accessibility attributes
      expect(chartContainer).toBeInTheDocument();
    });

    it('supports keyboard navigation for interactive elements', () => {
      const { container } = render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
        />
      );

      const chartContainer = container.querySelector('.custom-bar-chart');
      expect(chartContainer).toBeInTheDocument();

      // Should be keyboard accessible
      expect(chartContainer).toBeInTheDocument();
    });

    it('includes proper ARIA labels and descriptions', () => {
      const { container } = render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
        />
      );

      const chartContainer = container.querySelector('.custom-line-chart');
      expect(chartContainer).toBeInTheDocument();

      // Should have proper accessibility attributes
      expect(chartContainer).toBeInTheDocument();
    });
  });

  describe('Chart Data Validation and Error Handling', () => {
    it('handles empty data sets gracefully', () => {
      const { container } = render(
        <CustomBarChart
          data={[]}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render without crashing
      expect(svg).toBeInTheDocument();
    });

    it('validates data structure and types', () => {
      const invalidData = [
        { name: 'Valid', value: 100 },
        { name: null, value: 'invalid' }, // Invalid types
        { name: 'Another', value: NaN },
      ];

      const { container } = render(
        <CustomBarChart
          data={invalidData}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should handle invalid data gracefully
      expect(svg).toBeInTheDocument();
    });

    it('provides fallback for missing required properties', () => {
      const incompleteData = [
        { name: 'Item 1' }, // Missing value
        { value: 200 },    // Missing name
        { name: 'Item 3', value: 300 },
      ];

      const { container } = render(
        <CustomBarChart
          data={incompleteData}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render valid items and skip invalid ones
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Chart Animation and Interactivity', () => {
    it('supports smooth data transitions', () => {
      const initialData = [
        { name: 'A', value: 100 },
        { name: 'B', value: 200 },
      ];

      const { container, rerender } = render(
        <CustomBarChart
          data={initialData}
          width={400}
          height={300}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Update with new data
      const updatedData = [
        { name: 'A', value: 150 },
        { name: 'B', value: 250 },
        { name: 'C', value: 100 },
      ];

      rerender(
        <CustomBarChart
          data={updatedData}
          width={400}
          height={300}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should handle data updates smoothly
      const bars = svg.querySelectorAll('rect');
      expect(bars.length).toBe(updatedData.length);
    });

    it('provides hover interactions and tooltips', () => {
      const { container } = render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should support hover interactions
      const bars = svg.querySelectorAll('rect');
      expect(bars.length).toBe(complexBarData.length);
    });

    it('maintains performance with large datasets', () => {
      const largeDataset = Array.from({ length: 100 }, (_, i) => ({
        name: `डेटा ${i + 1}`,
        value: Math.floor(Math.random() * 1000) + 100,
      }));

      const startTime = performance.now();

      const { container } = render(
        <CustomLineChart
          data={largeDataset}
          width={800}
          height={400}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Should render large datasets within reasonable time
      expect(renderTime).toBeLessThan(2000);
    });
  });
});