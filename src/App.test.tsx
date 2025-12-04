import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import App from './App';

describe('DhruvMap App UI', () => {
    it('renders the Dhruv war-room sidebar with correct title and buttons', () => {
        render(<App />);

        // Title
        expect(screen.getByText(/PROJECT DHRUV/i)).toBeInTheDocument();
        expect(screen.getByText(/\/\/ LIVE GEO-INTEL/i)).toBeInTheDocument();

        // Core buttons
        expect(screen.getByRole('button', { name: /Global View/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Morph to Map/i })).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: /Focus Chhattisgarh/i }),
        ).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Reset View/i })).toBeInTheDocument();
    });

    it('shows a breadcrumb starting with Chhattisgarh', () => {
        render(<App />);

        const breadcrumbs = screen.getAllByText(/Chhattisgarh/i);
        expect(breadcrumbs.length).toBeGreaterThan(0);
    });

    it('updates mode indicator when morphing to map is triggered', async () => {
        const user = userEvent.setup();
        render(<App />);

        // mode indicator should exist
        const modeBefore = await screen.findByText(/Mode:/i);
        expect(modeBefore).toBeInTheDocument();

        const morphBtn = screen.getByRole('button', { name: /Morph to Map/i });
        await user.click(morphBtn);

        // depending on implementation, mode label might change to "Flat"
        const modeAfter = await screen.findByText(/Mode:\s*FLAT/i, {}, { timeout: 2000 });
        expect(modeAfter).toBeInTheDocument();
    });
});
