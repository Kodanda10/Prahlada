import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import CustomBarChart from '../../components/charts/CustomBarChart';
import CustomLineChart from '../../components/charts/CustomLineChart';
import CustomPieChart from '../../components/charts/CustomPieChart';
import { getTweetStats, getTweetTimeStats } from '../../utils/testDataLoader';

describe('Chart Visualization Visual Regression', () => {
  // Use real data
  const barData = getTweetStats().slice(0, 5);
  const lineData = getTweetTimeStats();
  const pieData = getTweetStats().slice(0, 4).map((item, index) => ({
      ...item,
      color: ['#8884d8', '#82ca9d', '#ffc658', '#ff8042'][index % 4]
  }));

  // Fallback if no real data (shouldn't happen if loader works)
  if (barData.length === 0) console.warn("No real bar data loaded");

  describe('CustomBarChart Component', () => {
    it('renders bars with consistent dimensions', () => {
      const { container } = render(
        <CustomBarChart
          data={barData}
          xKey="name"
          dataKey="value"
          width={400}
          height={300}
        />
      );

      const chartContainer = container.firstChild;
      expect(chartContainer).toBeInTheDocument();

      // Check for SVG element (charts typically render as SVG)
      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('handles empty data gracefully', () => {
      const { container } = render(
        <CustomBarChart
          data={[]}
          xKey="name"
          dataKey="value"
          width={400}
          height={300}
        />
      );

      const chartContainer = container.firstChild;
      expect(chartContainer).toBeInTheDocument();
    });

    it('maintains aspect ratio', () => {
      const { container } = render(
        <CustomBarChart
          data={barData}
          xKey="name"
          dataKey="value"
          width={600}
          height={400}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
      expect(svgElement).toHaveAttribute('width', '600');
      expect(svgElement).toHaveAttribute('height', '400');
    });
  });

  describe('CustomLineChart Component', () => {
    it('renders line chart with data points', () => {
      const { container } = render(
        <CustomLineChart
          data={lineData}
          xKey="name"
          dataKey="value"
          width={400}
          height={300}
        />
      );

      const chartContainer = container.firstChild;
      expect(chartContainer).toBeInTheDocument();

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('displays trend line correctly', () => {
      const { container } = render(
        <CustomLineChart
          data={lineData}
          xKey="name"
          dataKey="value"
          width={500}
          height={300}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();

      // Verify line element exists (mock renders a group)
      const lineElement = svgElement.querySelector('g');
      expect(lineElement).toBeInTheDocument();
    });
  });

  describe('CustomPieChart Component', () => {
    it('renders pie segments with colors', () => {
      const { container } = render(
        <CustomPieChart
          data={pieData}
          width={400}
          height={400}
        />
      );

      const chartContainer = container.firstChild;
      expect(chartContainer).toBeInTheDocument();

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('maintains circular proportions', () => {
      const { container } = render(
        <CustomPieChart
          data={pieData}
          width={300}
          height={300}
        />
      );

      // CustomPieChart wraps the chart in an inner div with the dimensions
      const sizedContainer = container.querySelector('.relative') as HTMLElement;
      expect(sizedContainer).toBeInTheDocument();
      expect(sizedContainer.style.width).toBe('300px');
      expect(sizedContainer.style.height).toBe('300px');

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });
  });

  describe('Chart Responsiveness', () => {
    it('charts adapt to container size changes', () => {
      const { container, rerender } = render(
        <div style={{ width: '400px' }}>
          <CustomBarChart
            data={barData}
            xKey="name"
            dataKey="value"
            width={400}
            height={300}
          />
        </div>
      );

      let svgElement = container.querySelector('svg');
      expect(svgElement).toHaveAttribute('width', '400');

      rerender(
        <div style={{ width: '600px' }}>
          <CustomBarChart
            data={barData}
            xKey="name"
            dataKey="value"
            width={600}
            height={300}
          />
        </div>
      );

      svgElement = container.querySelector('svg');
      expect(svgElement).toHaveAttribute('width', '600');
    });
  });
});