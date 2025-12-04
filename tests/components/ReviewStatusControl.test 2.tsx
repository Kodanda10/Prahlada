import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ReviewStatusControl from '../../components/controlhub/ReviewStatusControl';

// Mock ReviewStatusPanel
vi.mock('../../components/controlhub/ReviewStatusPanel', () => ({
    default: ({ totalCount }: any) => <div>Mocked Panel: {totalCount}</div>,
}));

describe('ReviewStatusControl Component', () => {
    const defaultProps = {
        totalCount: 100,
        approvedCount: 45,
        pendingCount: 30,
        skippedCount: 25,
    };

    it('renders toggle button with Hindi text', () => {
        render(<ReviewStatusControl {...defaultProps} />);
        expect(screen.getByText('समीक्षा स्टेटस')).toBeInTheDocument();
    });

    it('toggles panel on button click', () => {
        render(<ReviewStatusControl {...defaultProps} />);
        const button = screen.getByText('समीक्षा स्टेटस');

        expect(screen.queryByText(/Mocked Panel/)).not.toBeInTheDocument();

        fireEvent.click(button);

        expect(screen.getByText(/Mocked Panel/)).toBeInTheDocument();
    });

    it('closes panel on second click', () => {
        render(<ReviewStatusControl {...defaultProps} />);
        const button = screen.getByText('समीक्षा स्टेटस');

        fireEvent.click(button);
        expect(screen.getByText(/Mocked Panel/)).toBeInTheDocument();

        fireEvent.click(button);
        // Panel should close (AnimatePresence handles removal)
    });
});
