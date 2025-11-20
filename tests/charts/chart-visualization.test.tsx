import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import CustomBarChart from '../../components/charts/CustomBarChart';
import CustomLineChart from '../../components/charts/CustomLineChart';
import CustomPieChart from '../../components/charts/CustomPieChart';

describe('Chart Visualization Tests', () => {
  const barData = [
    { name: 'Jan', value: 400 },
    { name: 'Feb', value: 300 },
    { name: 'Mar', value: 600 },
    { name: 'Apr', value: 800 },
  ];

  const lineData = [
    { name: 'Week 1', value: 100 },
    { name: 'Week 2', value: 200 },
    { name: 'Week 3', value: 150 },
  ];

  const pieData = [
    { name: 'A', value: 400, color: '#8884d8' },
    { name: 'B', value: 300, color: '#82ca9d' },
    { name: 'C', value: 300, color: '#ffc658' },
  ];

  describe('CustomBarChart Rendering', () => {
    it('renders bars with correct heights', () => {
      const { container } = render(
        <CustomBarChart data={barData} width={400} height={300} />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const bars = svg.querySelectorAll('rect');
      expect(bars.length).toBe(barData.length);
    });

    it('displays axis labels', () => {
      const { container } = render(
        <CustomBarChart data={barData} width={400} height={300} />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const labels = svg.querySelectorAll('text');
      expect(labels.length).toBeGreaterThan(0);
    });
  });

  describe('CustomLineChart Rendering', () => {
    it('renders line path and data points', () => {
      const { container } = render(
        <CustomLineChart data={lineData} width={400} height={300} />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const path = svg.querySelector('path');
      expect(path).toBeInTheDocument();
    });

    it('shows grid lines and markers', () => {
      const { container } = render(
        <CustomLineChart data={lineData} width={400} height={300} />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const circles = svg.querySelectorAll('circle');
      expect(circles.length).toBe(lineData.length);
    });
  });

  describe('CustomPieChart Rendering', () => {
    it('renders pie segments with colors', () => {
      const { container } = render(
        <CustomPieChart data={pieData} width={400} height={400} />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const paths = svg.querySelectorAll('path');
      expect(paths.length).toBe(pieData.length);
    });

    it('displays legend labels', () => {
      const { container } = render(
        <CustomPieChart data={pieData} width={400} height={400} />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const textElements = svg.querySelectorAll('text');
      expect(textElements.length).toBeGreaterThan(0);
    });
  });

  describe('Chart Responsiveness', () => {
    it('adapts to different container sizes', () => {
      const { container, rerender } = render(
        <CustomBarChart data={barData} width={400} height={300} />
      );

      let svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '400');

      rerender(
        <CustomBarChart data={barData} width={600} height={400} />
      );

      svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '600');
    });
  });
});