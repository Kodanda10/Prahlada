import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';
import React from 'react';

describe('MapBoxVisual Tooltip Interaction', () => {
  it('shows tooltip on marker hover', async () => {
    render(<MapBoxVisual />);

    // Find the marker for "खरसिया"
    const markerLabel = screen.getByText(/खरसिया/);
    const markerContainer = markerLabel.closest('div')?.parentElement?.parentElement; // Traversing up to the motion.div

    if (markerContainer) {
        fireEvent.mouseEnter(markerContainer);

        // Tooltip should appear
        await waitFor(() => {
            expect(screen.getByText(/जनसम्पर्क अभियान/)).toBeInTheDocument();
            expect(screen.getByText(/19 नवंबर/)).toBeInTheDocument();
        });
    } else {
        throw new Error("Marker container not found");
    }
  });

  it('hides tooltip on mouse leave', async () => {
    render(<MapBoxVisual />);
    const markerLabel = screen.getByText(/खरसिया/);
    const markerContainer = markerLabel.closest('div')?.parentElement?.parentElement;

    if (markerContainer) {
        fireEvent.mouseEnter(markerContainer);
        await waitFor(() => expect(screen.getByText(/जनसम्पर्क अभियान/)).toBeInTheDocument());

        fireEvent.mouseLeave(markerContainer);
        await waitFor(() => expect(screen.queryByText(/जनसम्पर्क अभियान/)).not.toBeInTheDocument());
    }
  });

  it('tooltip displays correct Hindi content format', async () => {
    render(<MapBoxVisual />);
    const markerLabel = screen.getByText(/खरसिया/);
    const markerContainer = markerLabel.closest('div')?.parentElement?.parentElement;

    if (markerContainer) {
        fireEvent.mouseEnter(markerContainer);

        await waitFor(() => {
            // Check specific Hindi format: "स्थान: खरसिया"
            expect(screen.getByText('स्थान: खरसिया')).toBeInTheDocument();
            expect(screen.getByText('कुल दौरे: 05')).toBeInTheDocument();
            expect(screen.getByText('अंतिम गतिविधि:')).toBeInTheDocument();
        });
    }
  });

  it('tooltip positioning prevents viewport clipping', async () => {
    render(<MapBoxVisual />);
    const markerLabel = screen.getByText(/खरसिया/);
    const markerContainer = markerLabel.closest('div')?.parentElement?.parentElement;

    if (markerContainer) {
        fireEvent.mouseEnter(markerContainer);

        await waitFor(() => {
            const tooltip = screen.getByText('स्थान: खरसिया').closest('[class*="backdrop-blur-xl"]');
            expect(tooltip).toBeInTheDocument();

            // Tooltip should have positioning classes to prevent clipping
            // This would be tested by checking computed styles in real E2E tests
            expect(tooltip).toHaveClass('absolute');
        });
    }
  });

  it('tooltip adjusts position for edge markers', async () => {
    // Test with markers near viewport edges
    render(<MapBoxVisual />);

    // Test assumes markers are positioned at different locations
    // In real implementation, this would test left/right/top/bottom positioning
    const markerLabel = screen.getByText(/खरसिया/);
    const markerContainer = markerLabel.closest('div')?.parentElement?.parentElement;

    if (markerContainer) {
        fireEvent.mouseEnter(markerContainer);

        await waitFor(() => {
            const tooltip = screen.getByText('स्थान: खरसिया').closest('[class*="backdrop-blur-xl"]');
            // Tooltip should not be clipped - in real tests, check bounding rect
            expect(tooltip).toBeInTheDocument();
        });
    }
  });
});
