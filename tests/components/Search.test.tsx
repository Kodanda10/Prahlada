import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Search from '../../components/Search';
import { searchService } from '../../services/search';

// Mock the search service
vi.mock('../../services/search', () => ({
    searchService: {
        search: vi.fn(),
    },
}));

describe('Search Component', () => {
    const mockOnResultSelect = vi.fn();

    const mockResults = [
        {
            id: '1',
            title: 'मुख्यमंत्री दौरा',
            description: 'मुख्यमंत्री ने रायपुर का दौरा किया',
            category: 'दौरा',
            location: 'रायपुर',
        },
        {
            id: '2',
            title: 'शिक्षा बैठक',
            description: 'शिक्षा विभाग की बैठक',
            category: 'बैठक',
            location: null,
        },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    describe('Rendering', () => {
        it('renders search input', () => {
            render(<Search />);

            expect(screen.getByPlaceholderText('खोजें (Search)...')).toBeInTheDocument();
        });

        it('renders search icon', () => {
            const { container } = render(<Search />);

            const icon = container.querySelector('svg');
            expect(icon).toBeInTheDocument();
        });

        it('applies custom className', () => {
            const { container } = render(<Search className="custom-class" />);

            const wrapper = container.querySelector('.custom-class');
            expect(wrapper).toBeInTheDocument();
        });
    });

    describe('Search Input', () => {
        it('updates query on input change', () => {
            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...') as HTMLInputElement;
            fireEvent.change(input, { target: { value: 'मुख्यमंत्री' } });

            expect(input.value).toBe('मुख्यमंत्री');
        });

        it('shows loading spinner while searching', async () => {
            (searchService.search as any).mockImplementation(
                () => new Promise((resolve) => setTimeout(() => resolve(mockResults), 1000))
            );

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test query' } });

            // Fast-forward debounce timer
            vi.advanceTimersByTime(300);

            await waitFor(() => {
                const loader = screen.queryByRole('img', { hidden: true });
                // Loader2 component should be present
                expect(document.querySelector('.animate-spin')).toBeInTheDocument();
            });
        });

        it('debounces search by 300ms', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            expect(searchService.search).not.toHaveBeenCalled();

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(searchService.search).toHaveBeenCalledWith({ query: 'test' });
            });
        });

        it('does not search for queries shorter than 3 characters', async () => {
            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'ab' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(searchService.search).not.toHaveBeenCalled();
            });
        });

        it('searches when query is 3+ characters', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'abc' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(searchService.search).toHaveBeenCalledWith({ query: 'abc' });
            });
        });
    });

    describe('Search Results', () => {
        it('displays results after search', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test query' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('मुख्यमंत्री दौरा')).toBeInTheDocument();
                expect(screen.getByText('शिक्षा बैठक')).toBeInTheDocument();
            });
        });

        it('displays result descriptions', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('मुख्यमंत्री ने रायपुर का दौरा किया')).toBeInTheDocument();
            });
        });

        it('displays category badges', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('दौरा')).toBeInTheDocument();
                expect(screen.getByText('बैठक')).toBeInTheDocument();
            });
        });

        it('displays location when present', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('रायपुर')).toBeInTheDocument();
            });
        });

        it('does not render location badge when null', async () => {
            (searchService.search as any).mockResolvedValue([mockResults[1]]);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.queryByText('रायपुर')).not.toBeInTheDocument();
            });
        });

        it('hides results when query is cleared', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...') as HTMLInputElement;
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('मुख्यमंत्री दौरा')).toBeInTheDocument();
            });

            fireEvent.change(input, { target: { value: '' } });
            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.queryByText('मुख्यमंत्री दौरा')).not.toBeInTheDocument();
            });
        });
    });

    describe('Result Selection', () => {
        it('calls onResultSelect when result is clicked', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search onResultSelect={mockOnResultSelect} />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('मुख्यमंत्री दौरा')).toBeInTheDocument();
            });

            const result = screen.getByText('मुख्यमंत्री दौरा');
            fireEvent.click(result);

            expect(mockOnResultSelect).toHaveBeenCalledWith(mockResults[0]);
        });

        it('sets query to result title after selection', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search onResultSelect={mockOnResultSelect} />);

            const input = screen.getByPlaceholderText('खोजें (Search)...') as HTMLInputElement;
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('मुख्यमंत्री दौरा')).toBeInTheDocument();
            });

            const result = screen.getByText('मुख्यमंत्री दौरा');
            fireEvent.click(result);

            await waitFor(() => {
                expect(input.value).toBe('मुख्यमंत्री दौरा');
            });
        });

        it('hides results after selection', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            render(<Search onResultSelect={mockOnResultSelect} />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(screen.getByText('मुख्यमंत्री दौरा')).toBeInTheDocument();
            });

            const result = screen.getByText('मुख्यमंत्री दौरा');
            fireEvent.click(result);

            await waitFor(() => {
                expect(screen.queryByText('शिक्षा बैठक')).not.toBeInTheDocument();
            });
        });
    });

    describe('Error Handling', () => {
        it('handles search errors gracefully', async () => {
            (searchService.search as any).mockRejectedValue(new Error('Search failed'));

            const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

            render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                expect(consoleSpy).toHaveBeenCalledWith('Search error:', expect.any(Error));
            });

            consoleSpy.mockRestore();
        });
    });

    describe('Styling', () => {
        it('has rounded input field', () => {
            const { container } = render(<Search />);

            const input = container.querySelector('.rounded-full');
            expect(input).toBeInTheDocument();
        });

        it('applies focus styles', () => {
            const { container } = render(<Search />);

            const input = container.querySelector('input');
            expect(input).toHaveClass('focus:border-[#8BF5E6]');
        });

        it('has glassmorphism results dropdown', async () => {
            (searchService.search as any).mockResolvedValue(mockResults);

            const { container } = render(<Search />);

            const input = screen.getByPlaceholderText('खोजें (Search)...');
            fireEvent.change(input, { target: { value: 'test' } });

            vi.advanceTimersByTime(300);

            await waitFor(() => {
                const dropdown = container.querySelector('.backdrop-blur-xl');
                expect(dropdown).toBeInTheDocument();
            });
        });
    });
});
