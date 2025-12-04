import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PageLoader from '../../components/PageLoader';

describe('PageLoader Component', () => {
    describe('Rendering', () => {
        it('renders loader element', () => {
            render(<PageLoader />);

            const loader = screen.getByLabelText('Loading');
            expect(loader).toBeInTheDocument();
        });

        it('displays loading text in Hindi', () => {
            render(<PageLoader />);

            expect(screen.getByText(/लोड हो रहा है/i)).toBeInTheDocument();
        });

        it('applies spinner animation class', () => {
            const { container } = render(<PageLoader />);

            const spinner = container.querySelector('.animate-spin');
            expect(spinner).toBeInTheDocument();
        });
    });
});
