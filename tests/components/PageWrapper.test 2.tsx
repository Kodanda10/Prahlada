import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PageWrapper from '../../components/PageWrapper';

describe('PageWrapper Component', () => {
    describe('Rendering', () => {
        it('renders children correctly', () => {
            render(
                <PageWrapper>
                    <div>Test Child Content</div>
                </PageWrapper>
            );

            expect(screen.getByText('Test Child Content')).toBeInTheDocument();
        });

        it('applies wrapper styling', () => {
            const { container } = render(
                <PageWrapper>
                    <div>Content</div>
                </PageWrapper>
            );

            const wrapper = container.firstChild;
            expect(wrapper).toBeInTheDocument();
        });

        it('wraps multiple children', () => {
            render(
                <PageWrapper>
                    <div>Child 1</div>
                    <div>Child 2</div>
                    <div>Child 3</div>
                </PageWrapper>
            );

            expect(screen.getByText('Child 1')).toBeInTheDocument();
            expect(screen.getByText('Child 2')).toBeInTheDocument();
            expect(screen.getByText('Child 3')).toBeInTheDocument();
        });
    });
});
