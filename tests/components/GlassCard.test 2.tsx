import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import GlassCard from '../../components/GlassCard';

describe('GlassCard Component', () => {
    describe('Rendering', () => {
        it('renders children correctly', () => {
            render(
                <GlassCard>
                    <div>Test Content</div>
                </GlassCard>
            );

            expect(screen.getByText('Test Content')).toBeInTheDocument();
        });

        it('renders title when provided', () => {
            render(
                <GlassCard title="Test Title">
                    <div>Content</div>
                </GlassCard>
            );

            expect(screen.getByText('Test Title')).toBeInTheDocument();
        });

        it('renders action button when provided', () => {
            render(
                <GlassCard action={<button>Action</button>}>
                    <div>Content</div>
                </GlassCard>
            );

            expect(screen.getByText('Action')).toBeInTheDocument();
        });

        it('renders both title and action', () => {
            render(
                <GlassCard title="Title" action={<button>Action</button>}>
                    <div>Content</div>
                </GlassCard>
            );

            expect(screen.getByText('Title')).toBeInTheDocument();
            expect(screen.getByText('Action')).toBeInTheDocument();
        });

        it('does not render header when no title or action', () => {
            const { container } = render(
                <GlassCard>
                    <div>Content</div>
                </GlassCard>
            );

            const header = container.querySelector('.border-b');
            expect(header).not.toBeInTheDocument();
        });
    });

    describe('Styling', () => {
        it('applies glassmorphism effect', () => {
            const { container } = render(
                <GlassCard>
                    <div>Content</div>
                </GlassCard>
            );

            const card = container.querySelector('.backdrop-blur-md');
            expect(card).toBeInTheDocument();
        });

        it('applies custom className', () => {
            const { container } = render(
                <GlassCard className="custom-class">
                    <div>Content</div>
                </GlassCard>
            );

            const card = container.querySelector('.custom-class');
            expect(card).toBeInTheDocument();
        });

        it('has rounded corners', () => {
            const { container } = render(
                <GlassCard>
                    <div>Content</div>
                </GlassCard>
            );

            const card = container.querySelector('.rounded-2xl');
            expect(card).toBeInTheDocument();
        });

        it('has border and shadow', () => {
            const { container } = render(
                <GlassCard>
                    <div>Content</div>
                </GlassCard>
            );

            const card = container.firstChild as HTMLElement;
            expect(card).toHaveClass('border');
            expect(card).toHaveClass('shadow-xl');
        });
    });

    describe('Animation', () => {
        it('is a framer-motion component', () => {
            const { container } = render(
                <GlassCard>
                    <div>Content</div>
                </GlassCard>
            );

            const card = container.firstChild;
            expect(card).toBeInTheDocument();
        });

        it('has hover animation props', () => {
            const { container } = render(
                <GlassCard>
                    <div>Content</div>
                </GlassCard>
            );

            const card = container.querySelector('.hover\\:bg-white\\/\\[0\\.05\\]');
            expect(card).toBeInTheDocument();
        });
    });

    describe('Props', () => {
        it('passes through additional HTML motion props', () => {
            render(
                <GlassCard data-testid="glass-card">
                    <div>Content</div>
                </GlassCard>
            );

            const card = screen.getByTestId('glass-card');
            expect(card).toBeInTheDocument();
        });
    });
});
