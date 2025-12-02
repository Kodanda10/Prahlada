import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import TweetPreviewModal from '../../components/TweetPreviewModal';

describe('TweetPreviewModal Component', () => {
    const defaultProps = {
        isOpen: true,
        tweetId: '123456789',
        text: 'मुख्यमंत्री ने स्कूल का दौरा किया और विकास योजनाओं की समीक्षा की।',
        x: 100,
        y: 200,
    };

    describe('Rendering', () => {
        it('renders when isOpen is true', () => {
            render(<TweetPreviewModal {...defaultProps} />);

            expect(screen.getByText(defaultProps.text)).toBeInTheDocument();
        });

        it('does not render when isOpen is false', () => {
            render(<TweetPreviewModal {...defaultProps} isOpen={false} />);

            expect(screen.queryByText(defaultProps.text)).not.toBeInTheDocument();
        });

        it('displays tweet text in Hindi', () => {
            render(<TweetPreviewModal {...defaultProps} />);

            const textElement = screen.getByText(defaultProps.text);
            expect(textElement).toHaveClass('font-hindi');
        });

        it('renders Twitter user placeholder', () => {
            render(<TweetPreviewModal {...defaultProps} />);

            expect(screen.getByText('Twitter User')).toBeInTheDocument();
            expect(screen.getByText('@username')).toBeInTheDocument();
        });

        it('renders media placeholder', () => {
            render(<TweetPreviewModal {...defaultProps} />);

            expect(screen.getByText('मीडिया पूर्वावलोकन (Media Preview)')).toBeInTheDocument();
        });

        it('renders footer with timestamp', () => {
            render(<TweetPreviewModal {...defaultProps} />);

            expect(screen.getByText(/10:30 AM/)).toBeInTheDocument();
            expect(screen.getByText(/Twitter for Android/)).toBeInTheDocument();
        });
    });

    describe('Positioning', () => {
        it('positions modal at correct x, y coordinates', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} x={150} y={250} />);

            const modal = container.querySelector('[style*="position: fixed"]');
            expect(modal).toHaveStyle({
                left: '150px',
                top: '250px',
            });
        });

        it('sets correct z-index', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} />);

            const modal = container.querySelector('[style*="z-index"]');
            expect(modal).toHaveStyle({ zIndex: '100' });
        });
    });

    describe('Styling', () => {
        it('applies glassmorphism effect', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} />);

            const glassCard = container.querySelector('.backdrop-blur-xl');
            expect(glassCard).toBeInTheDocument();
        });

        it('has pointer-events-none class', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} />);

            const modal = container.querySelector('.pointer-events-none');
            expect(modal).toBeInTheDocument();
        });

        it('applies rounded corners', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} />);

            const card = container.querySelector('.rounded-2xl');
            expect(card).toBeInTheDocument();
        });
    });

    describe('Animation', () => {
        it('has framer-motion animation props', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} />);

            // Framer motion adds inline styles
            const motionDiv = container.querySelector('[style*="opacity"]');
            expect(motionDiv).toBeInTheDocument();
        });

        it('animates when opening', () => {
            const { rerender } = render(<TweetPreviewModal {...defaultProps} isOpen={false} />);

            rerender(<TweetPreviewModal {...defaultProps} isOpen={true} />);

            expect(screen.getByText(defaultProps.text)).toBeInTheDocument();
        });
    });

    describe('Edge Cases', () => {
        it('handles long text gracefully', () => {
            const longText = 'बहुत लंबा पाठ '.repeat(50);
            render(<TweetPreviewModal {...defaultProps} text={longText} />);

            expect(screen.getByText(longText)).toBeInTheDocument();
        });

        it('handles empty text', () => {
            render(<TweetPreviewModal {...defaultProps} text="" />);

            const textElement = screen.queryByText('');
            expect(textElement).not.toBeInTheDocument();
        });

        it('handles special characters in text', () => {
            const specialText = 'Test @mention #hashtag https://example.com';
            render(<TweetPreviewModal {...defaultProps} text={specialText} />);

            expect(screen.getByText(specialText)).toBeInTheDocument();
        });

        it('handles zero coordinates', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} x={0} y={0} />);

            const modal = container.querySelector('[style*="position: fixed"]');
            expect(modal).toHaveStyle({
                left: '0px',
                top: '0px',
            });
        });

        it('handles negative coordinates', () => {
            const { container } = render(<TweetPreviewModal {...defaultProps} x={-50} y={-100} />);

            const modal = container.querySelector('[style*="position: fixed"]');
            expect(modal).toHaveStyle({
                left: '-50px',
                top: '-100px',
            });
        });
    });
});
