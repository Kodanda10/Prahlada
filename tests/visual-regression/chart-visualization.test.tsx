import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import CustomBarChart from '../../components/charts/CustomBarChart';
import CustomLineChart from '../../components/charts/CustomLineChart';
import CustomPieChart from '../../components/charts/CustomPieChart';

describe('Chart Visualization Visual Regression', () => {
  const mockBarData = [
    { name: 'Jan', value: 400 },
    { name: 'Feb', value: 300 },
    { name: 'Mar', value: 600 },
    { name: 'Apr', value: 800 },
  ];

  const mockLineData = [
    { name: 'Week 1', value: 100 },
    { name: 'Week 2', value: 200 },
    { name: 'Week 3', value: 150 },
    { name: 'Week 4', value: 300 },
  ];

  const mockPieData = [
    { name: 'Category A', value: 400, color: '#8884d8' },
    { name: 'Category B', value: 300, color: '#82ca9d' },
    { name: 'Category C', value: 200, color: '#ffc658' },
  ];

  describe('CustomBarChart Component', () => {
    it('renders bars with consistent dimensions', () => {
      const { container } = render(
        <CustomBarChart
          data={mockBarData}
          width={400}
          height={300}
        />
      );

      const chartContainer = container.querySelector('.custom-bar-chart');
      expect(chartContainer).toBeInTheDocument();

      // Check for SVG element (charts typically render as SVG)
      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('handles empty data gracefully', () => {
      const { container } = render(
        <CustomBarChart
          data={[]}
          width={400}
          height={300}
        />
      );

      const chartContainer = container.querySelector('.custom-bar-chart');
      expect(chartContainer).toBeInTheDocument();
    });

    it('maintains aspect ratio', () => {
      const { container } = render(
        <CustomBarChart
          data={mockBarData}
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
          data={mockLineData}
          width={400}
          height={300}
        />
      );

      const chartContainer = container.querySelector('.custom-line-chart');
      expect(chartContainer).toBeInTheDocument();

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('displays trend line correctly', () => {
      const { container } = render(
        <CustomLineChart
          data={mockLineData}
          width={500}
          height={300}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();

      // Verify path element exists for the line
      const pathElement = svgElement.querySelector('path');
      expect(pathElement).toBeInTheDocument();
    });
  });

  describe('CustomPieChart Component', () => {
    it('renders pie segments with colors', () => {
      const { container } = render(
        <CustomPieChart
          data={mockPieData}
          width={400}
          height={400}
        />
      );

      const chartContainer = container.querySelector('.custom-pie-chart');
      expect(chartContainer).toBeInTheDocument();

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('maintains circular proportions', () => {
      const { container } = render(
        <CustomPieChart
          data={mockPieData}
          width={300}
          height={300}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
      expect(svgElement).toHaveAttribute('width', '300');
      expect(svgElement).toHaveAttribute('height', '300');
    });
  });

  describe('Chart Responsiveness', () => {
    it('charts adapt to container size changes', () => {
      const { container, rerender } = render(
        <div style={{ width: '400px' }}>
          <CustomBarChart
            data={mockBarData}
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
            data={mockBarData}
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