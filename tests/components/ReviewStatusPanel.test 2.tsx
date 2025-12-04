import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ReviewStatusPanel from '../../components/controlhub/ReviewStatusPanel';

// Mock the reviewStatusStore
vi.mock('../../utils/reviewStatusStore', () => ({
    useReviewStatus: () => ({
        showApproved: true,
        showPending: false,
        showSkipped: true,
        toggleApproved: vi.fn(),
        togglePending: vi.fn(),
        toggleSkipped: vi.fn(),
    }),
}));

describe('ReviewStatusPanel Component', () => {
    const defaultProps = {
        totalCount: 100,
        approvedCount: 45,
        pendingCount: 30,
        skippedCount: 25,
    };

    it('renders panel with Hindi title', () => {
        render(<ReviewStatusPanel {...defaultProps} />);
        expect(screen.getByText('समीक्षा स्थिति')).toBeInTheDocument();
    });

    it('displays total count', () => {
        render(<ReviewStatusPanel {...defaultProps} />);
        expect(screen.getByText('कुल ट्वीट्स')).toBeInTheDocument();
        expect(screen.getByText('100')).toBeInTheDocument();
    });

    it('displays approved count', () => {
        render(<ReviewStatusPanel {...defaultProps} />);
        expect(screen.getByText('स्वीकृत')).toBeInTheDocument();
        expect(screen.getByText('45')).toBeInTheDocument();
    });

    it('displays pending count', () => {
        render(<ReviewStatusPanel {...defaultProps} />);
        expect(screen.getByText('लंबित')).toBeInTheDocument();
        expect(screen.getByText('30')).toBeInTheDocument();
    });

    it('displays skipped count', () => {
        render(<ReviewStatusPanel {...defaultProps} />);
        expect(screen.getByText('स्किप्ड')).toBeInTheDocument();
        expect(screen.getByText('25')).toBeInTheDocument();
    });

    it('applies glassmorphism styling', () => {
        const { container } = render(<ReviewStatusPanel {...defaultProps} />);
        const panel = container.querySelector('.backdrop-blur-xl');
        expect(panel).toBeInTheDocument();
    });
});
