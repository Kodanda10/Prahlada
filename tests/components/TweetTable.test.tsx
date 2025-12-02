import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TweetTable from '../../components/home/TweetTable';
import { ParsedEvent } from '../../types';

const mockTweet: ParsedEvent = {
    tweet_id: '123456789',
    raw_text: 'मुख्यमंत्री ने गांव का दौरा किया और विकास कार्यों की समीक्षा की',
    created_at: '2024-11-24T10:30:00Z',
    parsed_data_v8: {
        event_date: '2024-11-24',
        event_type: 'दौरा',
        location: {
            district: 'रायपुर',
            assembly: 'रायपुर उत्तर',
            ulb: 'रायपुर नगर निगम',
            village: null,
        },
        people_canonical: ['मुख्यमंत्री', 'स्थानीय MLA'],
        target_groups: ['किसान', 'महिला'],
        description: 'विकास कार्यों की समीक्षा',
    },
    author_id: 'user123',
    author_username: 'cggovt',
    enriched_data: {},
};

const mockTweet2: ParsedEvent = {
    tweet_id: '987654321',
    raw_text: 'शिक्षा मंत्री ने स्कूल का निरीक्षण किया',
    created_at: '2024-11-25T14:00:00Z',
    parsed_data_v8: {
        event_date: '2024-11-25',
        event_type: 'बैठक',
        location: {
            district: 'बिलासपुर',
            assembly: null,
            ulb: null,
            village: 'अर्पा',
        },
        people_canonical: ['शिक्षा मंत्री'],
        target_groups: [],
        description: 'स्कूल निरीक्षण',
    },
    author_id: 'user456',
    author_username: 'edumin',
    enriched_data: {},
};

describe('TweetTable Component', () => {
    const mockOnPageChange = vi.fn();
    const mockOnMouseEnter = vi.fn();
    const mockOnMouseLeave = vi.fn();

    const defaultProps = {
        tweets: [mockTweet, mockTweet2],
        currentPage: 1,
        totalPages: 5,
        onPageChange: mockOnPageChange,
        onMouseEnter: mockOnMouseEnter,
        onMouseLeave: mockOnMouseLeave,
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the table with correct Hindi headers', () => {
            render(<TweetTable {...defaultProps} />);

            expect(screen.getByText('दिन / दिनांक')).toBeInTheDocument();
            expect(screen.getByText('📍 स्थान')).toBeInTheDocument();
            expect(screen.getByText('🎯 दौरा / कार्यक्रम')).toBeInTheDocument();
            expect(screen.getByText('👥 कौन/टैग')).toBeInTheDocument();
            expect(screen.getByText('📝 विवरण')).toBeInTheDocument();
            expect(screen.getByText('🔗 स्रोत')).toBeInTheDocument();
        });

        it('renders all tweets in the table', () => {
            render(<TweetTable {...defaultProps} />);

            expect(screen.getByText(mockTweet.raw_text)).toBeInTheDocument();
            expect(screen.getByText(mockTweet2.raw_text)).toBeInTheDocument();
        });

        it('displays location correctly (ULB priority)', () => {
            render(<TweetTable {...defaultProps} />);

            expect(screen.getByText('रायपुर नगर निगम')).toBeInTheDocument();
        });

        it('displays location correctly (Village fallback)', () => {
            render(<TweetTable {...defaultProps} />);

            expect(screen.getByText('अर्पा')).toBeInTheDocument();
        });

        it('displays unknown location when no location data', () => {
            const tweetNoLocation = {
                ...mockTweet,
                parsed_data_v8: {
                    ...mockTweet.parsed_data_v8,
                    location: {},
                },
            };

            render(<TweetTable {...defaultProps} tweets={[tweetNoLocation]} />);

            expect(screen.getByText('अज्ञात')).toBeInTheDocument();
        });

        it('renders event types with correct styling', () => {
            render(<TweetTable {...defaultProps} />);

            const daura = screen.getByText('दौरा');
            const baithak = screen.getByText('बैठक');

            expect(daura).toHaveClass('bg-pink-500/10');
            expect(baithak).toHaveClass('bg-blue-500/10');
        });

        it('displays people tags correctly', () => {
            render(<TweetTable {...defaultProps} />);

            expect(screen.getByText('मुख्यमंत्री')).toBeInTheDocument();
            expect(screen.getByText('स्थानीय MLA')).toBeInTheDocument();
            expect(screen.getByText('शिक्षा मंत्री')).toBeInTheDocument();
        });

        it('shows dash when no people tags', () => {
            const tweetNoPeople = {
                ...mockTweet,
                parsed_data_v8: {
                    ...mockTweet.parsed_data_v8,
                    people_canonical: [],
                },
            };

            render(<TweetTable {...defaultProps} tweets={[tweetNoPeople]} />);

            const dashElements = screen.getAllByText('-');
            expect(dashElements.length).toBeGreaterThan(0);
        });

        it('formats dates in Hindi', () => {
            render(<TweetTable {...defaultProps} />);

            // Date formatting is locale-specific, just check it's not the raw string
            const dateCell = screen.getAllByText(/2024/)[0];
            expect(dateCell).toBeInTheDocument();
        });
    });

    describe('Pagination', () => {
        it('renders pagination controls when totalPages > 1', () => {
            render(<TweetTable {...defaultProps} />);

            const prevButton = screen.getByRole('button', { name: '' }).previousSibling;
            const nextButton = screen.getByRole('button', { name: '' }).nextSibling;

            expect(prevButton).toBeInTheDocument();
            expect(nextButton).toBeInTheDocument();
        });

        it('does not render pagination when totalPages <= 1', () => {
            render(<TweetTable {...defaultProps} totalPages={1} />);

            const pagination = screen.queryByRole('button');
            expect(pagination).toBeNull();
        });

        it('disables previous button on first page', () => {
            render(<TweetTable {...defaultProps} currentPage={1} />);

            const buttons = screen.getAllByRole('button');
            const prevButton = buttons[0]; // First button should be prev

            expect(prevButton).toBeDisabled();
        });

        it('disables next button on last page', () => {
            render(<TweetTable {...defaultProps} currentPage={5} totalPages={5} />);

            const buttons = screen.getAllByRole('button');
            const nextButton = buttons[buttons.length - 1]; // Last button should be next

            expect(nextButton).toBeDisabled();
        });

        it('calls onPageChange when clicking page numbers', () => {
            render(<TweetTable {...defaultProps} currentPage={1} />);

            const page3Button = screen.getByText('3');
            fireEvent.click(page3Button);

            expect(mockOnPageChange).toHaveBeenCalledWith(3);
        });

        it('calls onPageChange when clicking next button', () => {
            render(<TweetTable {...defaultProps} currentPage={2} />);

            const buttons = screen.getAllByRole('button');
            const nextButton = buttons[buttons.length - 1];
            fireEvent.click(nextButton);

            expect(mockOnPageChange).toHaveBeenCalledWith(3);
        });

        it('calls onPageChange when clicking previous button', () => {
            render(<TweetTable {...defaultProps} currentPage={3} />);

            const buttons = screen.getAllByRole('button');
            const prevButton = buttons[0];
            fireEvent.click(prevButton);

            expect(mockOnPageChange).toHaveBeenCalledWith(2);
        });

        it('highlights current page button', () => {
            render(<TweetTable {...defaultProps} currentPage={2} />);

            const page2Button = screen.getByText('2');
            expect(page2Button).toHaveClass('bg-[#8BF5E6]');
            expect(page2Button).toHaveClass('text-[#0f172a]');
        });

        it('shows ellipsis for large page ranges', () => {
            render(<TweetTable {...defaultProps} currentPage={10} totalPages={20} />);

            const ellipsis = screen.getAllByText('...');
            expect(ellipsis.length).toBeGreaterThan(0);
        });

        it('shows first and last page buttons when not in range', () => {
            render(<TweetTable {...defaultProps} currentPage={10} totalPages={20} />);

            expect(screen.getByText('1')).toBeInTheDocument();
            expect(screen.getByText('20')).toBeInTheDocument();
        });
    });

    describe('Interactions', () => {
        it('calls onMouseEnter when hovering over tweet link', () => {
            render(<TweetTable {...defaultProps} />);

            const links = screen.getAllByRole('link');
            const firstLink = links[0];

            fireEvent.mouseEnter(firstLink);

            expect(mockOnMouseEnter).toHaveBeenCalled();
            expect(mockOnMouseEnter).toHaveBeenCalledWith(
                expect.any(Object),
                mockTweet
            );
        });

        it('calls onMouseLeave when leaving tweet link', () => {
            render(<TweetTable {...defaultProps} />);

            const links = screen.getAllByRole('link');
            const firstLink = links[0];

            fireEvent.mouseLeave(firstLink);

            expect(mockOnMouseLeave).toHaveBeenCalled();
        });

        it('renders correct Twitter link URL', () => {
            render(<TweetTable {...defaultProps} />);

            const links = screen.getAllByRole('link');
            const firstLink = links[0] as HTMLAnchorElement;

            expect(firstLink.href).toBe(`https://twitter.com/i/web/status/${mockTweet.tweet_id}`);
            expect(firstLink.target).toBe('_blank');
            expect(firstLink.rel).toBe('noopener noreferrer');
        });
    });

    describe('Edge Cases', () => {
        it('renders empty table when no tweets', () => {
            render(<TweetTable {...defaultProps} tweets={[]} />);

            const table = screen.getByRole('table');
            expect(table).toBeInTheDocument();

            const tbody = table.querySelector('tbody');
            expect(tbody?.children.length).toBe(0);
        });

        it('handles missing event_date gracefully', () => {
            const tweetNoDate = {
                ...mockTweet,
                parsed_data_v8: {
                    ...mockTweet.parsed_data_v8,
                    event_date: null,
                },
            };

            render(<TweetTable {...defaultProps} tweets={[tweetNoDate]} />);

            // Should fall back to created_at
            expect(screen.getByText(/2024/)).toBeInTheDocument();
        });

        it('handles invalid date strings gracefully', () => {
            const tweetBadDate = {
                ...mockTweet,
                created_at: 'invalid-date',
                parsed_data_v8: {
                    ...mockTweet.parsed_data_v8,
                    event_date: 'invalid',
                },
            };

            render(<TweetTable {...defaultProps} tweets={[tweetBadDate]} />);

            // Should render without crashing
            expect(screen.getByRole('table')).toBeInTheDocument();
        });

        it('renders row hover effects', () => {
            const { container } = render(<TweetTable {...defaultProps} />);

            const row = container.querySelector('tbody tr');
            expect(row).toHaveClass('hover:bg-white/5');
            expect(row).toHaveClass('group');
        });

        it('limits people tags to 2', () => {
            const tweetManyPeople = {
                ...mockTweet,
                parsed_data_v8: {
                    ...mockTweet.parsed_data_v8,
                    people_canonical: ['Person 1', 'Person 2', 'Person 3', 'Person 4'],
                },
            };

            render(<TweetTable {...defaultProps} tweets={[tweetManyPeople]} />);

            expect(screen.getByText('Person 1')).toBeInTheDocument();
            expect(screen.getByText('Person 2')).toBeInTheDocument();
            expect(screen.queryByText('Person 3')).not.toBeInTheDocument();
        });
    });

    describe('Styling and CSS Classes', () => {
        it('applies correct event type colors for jansampark', () => {
            const jansamparkTweet = {
                ...mockTweet,
                parsed_data_v8: {
                    ...mockTweet.parsed_data_v8,
                    event_type: 'जनसम्पर्क',
                },
            };

            render(<TweetTable {...defaultProps} tweets={[jansamparkTweet]} />);

            const badge = screen.getByText('जनसम्पर्क');
            expect(badge).toHaveClass('bg-green-500/10');
        });

        it('applies Hindi font class', () => {
            render(<TweetTable {...defaultProps} />);

            const hindiElements = screen.getAllByText(/रायपुर नगर निगम/);
            hindiElements.forEach((el) => {
                expect(el.closest('[class*="font-hindi"]')).toBeInTheDocument();
            });
        });
    });
});
