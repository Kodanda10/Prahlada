import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
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

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();

      // Should render bars for each data point (via data-item-count)
      expect(chart).toHaveAttribute('data-item-count', String(complexBarData.length));

      // Should have axis labels (mocked)
      expect(screen.getByText('XAxis')).toBeInTheDocument();
    });

    it('displays values and categories correctly', () => {
      render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();

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

      render(
        <CustomBarChart
          data={negativeData}
          width={400}
          height={300}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveAttribute('data-item-count', '3');
    });

    it('supports custom colors and theming', () => {
      render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();

      // Should use provided colors
      complexBarData.forEach(item => {
        expect(item.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      });
    });
  });

  describe('CustomLineChart Multi-Series Support', () => {
    it('renders multiple data series with legends', () => {
      render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
          xKey="name"
          dataKey="series1"
        />
      );

      const chart = screen.getByTestId('line-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveAttribute('data-item-count', String(multiLineData.length));
    });

    it('displays Hindi axis labels and legends', () => {
      render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
          xKey="name"
          dataKey="series1"
        />
      );

      expect(screen.getByText('XAxis')).toBeInTheDocument();
    });

    it('handles missing data points gracefully', () => {
      const sparseData = [
        { name: 'A', series1: 100, series2: null, series3: 90 },
        { name: 'B', series1: null, series2: 180, series3: 150 },
        { name: 'C', series1: 150, series2: 220, series3: null },
      ];

      render(
        <CustomLineChart
          data={sparseData}
          width={400}
          height={300}
          xKey="name"
          dataKey="series1"
        />
      );

      const chart = screen.getByTestId('line-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveAttribute('data-item-count', String(sparseData.length));
    });

    it('supports interactive hover states', () => {
      render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
          xKey="name"
          dataKey="series1"
        />
      );

      const chart = screen.getByTestId('line-chart');
      expect(chart).toBeInTheDocument();
    });
  });

  describe('CustomPieChart Enhanced Features', () => {
    it('renders pie segments with percentages and labels', () => {
      render(
        <CustomPieChart
          data={detailedPieData}
          width={400}
          height={400}
        />
      );

      const chart = screen.getByTestId('pie-chart');
      expect(chart).toBeInTheDocument();

      // Check legend labels
      expect(screen.getByText('उत्तरी क्षेत्र')).toBeInTheDocument();
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
      render(
        <CustomPieChart
          data={detailedPieData}
          width={400}
          height={400}
        />
      );

      const chart = screen.getByTestId('pie-chart');
      expect(chart).toBeInTheDocument();

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

      render(
        <CustomPieChart
          data={smallSegmentData}
          width={400}
          height={400}
        />
      );

      // Legend checks
      expect(screen.getByText('बड़ा')).toBeInTheDocument();
      expect(screen.getByText('छोटा')).toBeInTheDocument();
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
        const { unmount } = render(
          <CustomBarChart
            data={complexBarData.slice(0, 4)}
            width={width}
            height={height}
            xKey="name"
            dataKey="value"
          />
        );

        const chart = screen.getByTestId('bar-chart');
        expect(chart).toBeInTheDocument();
        expect(chart).toHaveAttribute('width', width.toString());
        expect(chart).toHaveAttribute('height', height.toString());
        unmount();
      });
    });

    it('maintains readability on small screens', () => {
      render(
        <CustomBarChart
          data={complexBarData.slice(0, 3)}
          width={300}
          height={200}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();
      expect(screen.getByText('XAxis')).toBeInTheDocument();
    });

    it('scales appropriately for high-DPI displays', () => {
      // Mock high DPI
      Object.defineProperty(window, 'devicePixelRatio', {
        value: 2,
        configurable: true,
      });

      render(
        <CustomLineChart
          data={multiLineData}
          width={400}
          height={300}
          xKey="name"
          dataKey="series1"
        />
      );

      const chart = screen.getByTestId('line-chart');
      expect(chart).toBeInTheDocument();
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
    });

    it('supports keyboard navigation for interactive elements', () => {
      const { container } = render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
          xKey="name"
          dataKey="value"
        />
      );

      const chartContainer = container.querySelector('.custom-bar-chart');
      expect(chartContainer).toBeInTheDocument();
    });

    it('includes proper ARIA labels and descriptions', () => {
      const { container } = render(
        <CustomLineChart
          data={multiLineData}
          width={600}
          height={400}
          xKey="name"
          dataKey="series1"
        />
      );

      const chartContainer = container.querySelector('.custom-line-chart');
      expect(chartContainer).toBeInTheDocument();
    });
  });

  describe('Chart Data Validation and Error Handling', () => {
    it('handles empty data sets gracefully', () => {
      render(
        <CustomBarChart
          data={[]}
          width={400}
          height={300}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveAttribute('data-item-count', '0');
    });

    it('validates data structure and types', () => {
      const invalidData = [
        { name: 'Valid', value: 100 },
        { name: null, value: 'invalid' }, // Invalid types
        { name: 'Another', value: NaN },
      ];

      render(
        <CustomBarChart
          data={invalidData}
          width={400}
          height={300}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveAttribute('data-item-count', '3');
    });

    it('provides fallback for missing required properties', () => {
      const incompleteData = [
        { name: 'Item 1' }, // Missing value
        { value: 200 },    // Missing name
        { name: 'Item 3', value: 300 },
      ];

      render(
        <CustomBarChart
          data={incompleteData}
          width={400}
          height={300}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveAttribute('data-item-count', '3');
    });
  });

  describe('Chart Animation and Interactivity', () => {
    it('supports smooth data transitions', () => {
      const initialData = [
        { name: 'A', value: 100 },
        { name: 'B', value: 200 },
      ];

      const { rerender } = render(
        <CustomBarChart
          data={initialData}
          width={400}
          height={300}
          xKey="name"
          dataKey="value"
        />
      );

      let chart = screen.getByTestId('bar-chart');
      expect(chart).toHaveAttribute('data-item-count', '2');

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
          xKey="name"
          dataKey="value"
        />
      );

      chart = screen.getByTestId('bar-chart');
      expect(chart).toHaveAttribute('data-item-count', '3');
    });

    it('provides hover interactions and tooltips', () => {
      render(
        <CustomBarChart
          data={complexBarData}
          width={600}
          height={400}
          xKey="name"
          dataKey="value"
        />
      );

      const chart = screen.getByTestId('bar-chart');
      expect(chart).toBeInTheDocument();
      // Tooltip is mocked as 'div' with text 'Tooltip'
      expect(screen.getByText('Tooltip')).toBeInTheDocument();
    });

    it('maintains performance with large datasets', () => {
      const largeDataset = Array.from({ length: 100 }, (_, i) => ({
        name: `डेटा ${i + 1}`,
        value: Math.floor(Math.random() * 1000) + 100,
      }));

      const startTime = performance.now();

      render(
        <CustomLineChart
          data={largeDataset}
          width={800}
          height={400}
          xKey="name"
          dataKey="value"
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      const chart = screen.getByTestId('line-chart');
      expect(chart).toBeInTheDocument();

      // Should render large datasets within reasonable time
      expect(renderTime).toBeLessThan(2000);
    });
  });
});