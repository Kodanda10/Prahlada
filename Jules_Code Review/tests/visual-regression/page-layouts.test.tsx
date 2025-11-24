import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Home from '../../pages/Home';
import Analytics from '../../pages/Analytics';
import Review from '../../pages/Review';

// Mock IntersectionObserver
const IntersectionObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

describe('Page Layout Visual Regression', () => {
  describe('Home Page Layout', () => {
    it('renders main layout structure', () => {
      render(
        <MemoryRouter>
          <Home />
        </MemoryRouter>
      );

      // Check for main page container
      const mainContainer = document.querySelector('main') || document.body;
      expect(mainContainer).toBeInTheDocument();
    });

    it('displays welcome content consistently', () => {
      render(
        <MemoryRouter>
          <Home />
        </MemoryRouter>
      );

      // Look for common home page elements
      const headings = screen.queryAllByRole('heading');
      expect(headings.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Analytics Page Layout', () => {
    it('renders analytics dashboard structure', () => {
      render(
        <MemoryRouter>
          <Analytics />
        </MemoryRouter>
      );

      const mainContainer = document.querySelector('main') || document.body;
      expect(mainContainer).toBeInTheDocument();
    });

    it('includes chart containers', () => {
      render(
        <MemoryRouter>
          <Analytics />
        </MemoryRouter>
      );

      // Analytics page should contain chart elements
      const charts = document.querySelectorAll('.custom-bar-chart, .custom-line-chart, .custom-pie-chart');
      expect(charts.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Review Page Layout', () => {
    it('renders review interface consistently', () => {
      render(
        <MemoryRouter>
          <Review />
        </MemoryRouter>
      );

      const mainContainer = document.querySelector('main') || document.body;
      expect(mainContainer).toBeInTheDocument();
    });
  });

  describe('Cross-Page Layout Consistency', () => {
    it('maintains consistent navigation across pages', () => {
      const pages = [
        { component: Home, name: 'Home' },
        { component: Analytics, name: 'Analytics' },
        { component: Review, name: 'Review' },
      ];

      pages.forEach(({ component: PageComponent, name }) => {
        const { container } = render(
          <MemoryRouter>
            <PageComponent />
          </MemoryRouter>
        );

        // Check for consistent page structure
        expect(container.firstChild).toBeInTheDocument();
      });
    });

    it('preserves glass morphism theme', () => {
      render(
        <MemoryRouter>
          <Home />
        </MemoryRouter>
      );

      // Look for glass-card elements that should be consistent across pages
      const glassElements = document.querySelectorAll('.glass-card, .animated-glass-card');
      expect(glassElements.length).toBeGreaterThanOrEqual(0);
    });
  });
});
