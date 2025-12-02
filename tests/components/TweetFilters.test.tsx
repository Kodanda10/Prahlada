import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TweetFilters from '../../components/home/TweetFilters';

describe('TweetFilters Component', () => {
    const mockSetLocationFilter = vi.fn();
    const mockSetTagFilter = vi.fn();
    const mockSetDateFrom = vi.fn();
    const mockSetDateTo = vi.fn();
    const mockOnClearFilters = vi.fn();

    const defaultProps = {
        locationFilter: '',
        setLocationFilter: mockSetLocationFilter,
        tagFilter: '',
        setTagFilter: mockSetTagFilter,
        dateFrom: '',
        setDateFrom: mockSetDateFrom,
        dateTo: '',
        setDateTo: mockSetDateTo,
        totalCount: 100,
        filteredCount: 100,
        onClearFilters: mockOnClearFilters,
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders all filter inputs', () => {
            render(<TweetFilters {...defaultProps} />);

            expect(screen.getByPlaceholderText('स्थान फ़िल्टर...')).toBeInTheDocument();
            expect(screen.getByPlaceholderText('टैग/मेंशन फ़िल्टर...')).toBeInTheDocument();
            expect(screen.getByText('तिथि से')).toBeInTheDocument();
            expect(screen.getByText('तिथि तक')).toBeInTheDocument();
        });

        it('renders clear filters button', () => {
            render(<TweetFilters {...defaultProps} />);

            expect(screen.getByText('फ़िल्टर साफ़ करें')).toBeInTheDocument();
        });

        it('displays count correctly', () => {
            render(<TweetFilters {...defaultProps} totalCount={500} filteredCount={250} />);

            expect(screen.getByText('250')).toBeInTheDocument();
            expect(screen.getByText('/ 500')).toBeInTheDocument();
        });

        it('displays filter icons', () => {
            const { container } = render(<TweetFilters {...defaultProps} />);

            const icons = container.querySelectorAll('svg');
            expect(icons.length).toBeGreaterThan(0);
        });
    });

    describe('Location Filter', () => {
        it('calls setLocationFilter on input change', () => {
            render(<TweetFilters {...defaultProps} />);

            const input = screen.getByPlaceholderText('स्थान फ़िल्टर...') as HTMLInputElement;
            fireEvent.change(input, { target: { value: 'रायपुर' } });

            expect(mockSetLocationFilter).toHaveBeenCalledWith('रायपुर');
        });


        it('displays current location filter value', () => {
            render(<TweetFilters {...defaultProps} locationFilter="बिलासपुर" />);

            const input = screen.getByPlaceholderText('स्थान फ़िल्टर...') as HTMLInputElement;
            expect(input.value).toBe('बिलासपुर');
        });

        it('has correct placeholder in Hindi', () => {
            render(<TweetFilters {...defaultProps} />);

            const input = screen.getByPlaceholderText('स्थान फ़िल्टर...');
            expect(input).toBeInTheDocument();
        });
    });

    describe('Tag Filter', () => {
        it('calls setTagFilter on input change', () => {
            render(<TweetFilters {...defaultProps} />);

            const input = screen.getByPlaceholderText('टैग/मेंशन फ़िल्टर...') as HTMLInputElement;
            fireEvent.change(input, { target: { value: 'मुख्यमंत्री' } });

            expect(mockSetTagFilter).toHaveBeenCalledWith('मुख्यमंत्री');
        });

        it('displays current tag filter value', () => {
            render(<TweetFilters {...defaultProps} tagFilter="शिक्षा मंत्री" />);

            const input = screen.getByPlaceholderText('टैग/मेंशन फ़िल्टर...') as HTMLInputElement;
            expect(input.value).toBe('शिक्षा मंत्री');
        });
    });

    describe('Date Filters', () => {
        it('calls setDateFrom on date input change', () => {
            render(<TweetFilters {...defaultProps} />);

            const inputs = screen.getAllByPlaceholderText('dd/mm/yyyy');
            const dateFromInput = inputs[0];

            fireEvent.change(dateFromInput, { target: { value: '2024-01-01' } });

            expect(mockSetDateFrom).toHaveBeenCalledWith('2024-01-01');
        });

        it('calls setDateTo on date input change', () => {
            render(<TweetFilters {...defaultProps} />);

            const inputs = screen.getAllByPlaceholderText('dd/mm/yyyy');
            const dateToInput = inputs[1];

            fireEvent.change(dateToInput, { target: { value: '2024-12-31' } });

            expect(mockSetDateTo).toHaveBeenCalledWith('2024-12-31');
        });

        it('displays current dateFrom value', () => {
            render(<TweetFilters {...defaultProps} dateFrom="2024-06-01" />);

            const inputs = screen.getAllByPlaceholderText('dd/mm/yyyy');
            const dateFromInput = inputs[0] as HTMLInputElement;

            expect(dateFromInput.value).toBe('2024-06-01');
        });

        it('displays current dateTo value', () => {
            render(<TweetFilters {...defaultProps} dateTo="2024-06-30" />);

            const inputs = screen.getAllByPlaceholderText('dd/mm/yyyy');
            const dateToInput = inputs[1] as HTMLInputElement;

            expect(dateToInput.value).toBe('2024-06-30');
        });

        it('renders Hindi labels for date inputs', () => {
            render(<TweetFilters {...defaultProps} />);

            expect(screen.getByText('तिथि से')).toBeInTheDocument();
            expect(screen.getByText('तिथि तक')).toBeInTheDocument();
        });
    });

    describe('Clear Filters Button', () => {
        it('calls onClearFilters when clicked', () => {
            render(<TweetFilters {...defaultProps} />);

            const clearButton = screen.getByText('फ़िल्टर साफ़ करें');
            fireEvent.click(clearButton);

            expect(mockOnClearFilters).toHaveBeenCalled();
        });

        it('has correct styling', () => {
            render(<TweetFilters {...defaultProps} />);

            const clearButton = screen.getByText('फ़िल्टर साफ़ करें');

            expect(clearButton).toHaveClass('bg-red-500/10');
            expect(clearButton).toHaveClass('text-red-400');
        });
    });

    describe('Count Display', () => {
        it('shows filtered count when filters are active', () => {
            render(<TweetFilters {...defaultProps} totalCount={1000} filteredCount={250} />);

            expect(screen.getByText('दिखा रहे हैं:')).toBeInTheDocument();
            expect(screen.getByText('250')).toBeInTheDocument();
            expect(screen.getByText('/ 1000')).toBeInTheDocument();
        });

        it('updates count display reactively', () => {
            const { rerender } = render(<TweetFilters {...defaultProps} totalCount={100} filteredCount={100} />);

            expect(screen.getByText('100')).toBeInTheDocument();

            rerender(<TweetFilters {...defaultProps} totalCount={100} filteredCount={50} />);

            expect(screen.getByText('50')).toBeInTheDocument();
        });

        it('displays count with Hindi text', () => {
            render(<TweetFilters {...defaultProps} />);

            const countText = screen.getByText('दिखा रहे हैं:');
            expect(countText).toHaveClass('font-hindi');
        });
    });

    describe('Styling and Accessibility', () => {
        it('applies Hindi font class to all inputs', () => {
            const { container } = render(<TweetFilters {...defaultProps} />);

            const inputs = container.querySelectorAll('input');
            inputs.forEach((input) => {
                expect(input).toHaveClass('font-hindi');
            });
        });

        it('has focus states for inputs', () => {
            const { container } = render(<TweetFilters {...defaultProps} />);

            const inputs = container.querySelectorAll('input');
            inputs.forEach((input) => {
                expect(input).toHaveClass('focus:border-[#8BF5E6]');
            });
        });

        it('has hover effects on icons', () => {
            const { container } = render(<TweetFilters {...defaultProps} />);

            const iconContainers = container.querySelectorAll('.group');
            expect(iconContainers.length).toBeGreaterThan(0);
        });

        it('makes inputs responsive with flex layout', () => {
            const { container } = render(<TweetFilters {...defaultProps} />);

            const filterContainer = container.querySelector('.flex-wrap');
            expect(filterContainer).toBeInTheDocument();
        });
    });

    describe('Edge Cases', () => {
        it('handles zero counts gracefully', () => {
            render(<TweetFilters {...defaultProps} totalCount={0} filteredCount={0} />);

            expect(screen.getByText('0')).toBeInTheDocument();
            expect(screen.getByText('/ 0')).toBeInTheDocument();
        });

        it('handles empty filter values', () => {
            render(<TweetFilters {...defaultProps}
                locationFilter=""
                tagFilter=""
                dateFrom=""
                dateTo=""
            />);

            const locationInput = screen.getByPlaceholderText('स्थान फ़िल्टर...') as HTMLInputElement;
            const tagInput = screen.getByPlaceholderText('टैग/मेंशन फ़िल्टर...') as HTMLInputElement;

            expect(locationInput.value).toBe('');
            expect(tagInput.value).toBe('');
        });

        it('handles large count numbers', () => {
            render(<TweetFilters {...defaultProps} totalCount={999999} filteredCount={123456} />);

            expect(screen.getByText('123456')).toBeInTheDocument();
            expect(screen.getByText('/ 999999')).toBeInTheDocument();
        });

        it('handles special characters in filter values', () => {
            render(<TweetFilters {...defaultProps}
                locationFilter="रायपुर (urban)"
                tagFilter="मुख्यमंत्री @cg"
            />);

            const locationInput = screen.getByPlaceholderText('स्थान फ़िल्टर...') as HTMLInputElement;
            const tagInput = screen.getByPlaceholderText('टैग/मेंशन फ़िल्टर...') as HTMLInputElement;

            expect(locationInput.value).toContain('(urban)');
            expect(tagInput.value).toContain('@cg');
        });
    });
});
