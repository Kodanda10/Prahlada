import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import LocationFeed from '../src/components/LocationFeed';

describe('LocationFeed', () => {
    const mockLocations = [
        { id: 'raipur', name: 'Raipur', type: 'district', lat: 21.25, lon: 81.63 },
        { id: 'bilaspur', name: 'Bilaspur', type: 'district', lat: 22.08, lon: 82.14 },
    ];

    it('renders the list of locations', () => {
        render(<LocationFeed locations={mockLocations} onSelect={vi.fn()} />);

        expect(screen.getByText('Raipur')).toBeInTheDocument();
        expect(screen.getByText('Bilaspur')).toBeInTheDocument();
    });

    it('calls onSelect when a location is clicked', () => {
        const handleSelect = vi.fn();
        render(<LocationFeed locations={mockLocations} onSelect={handleSelect} />);

        fireEvent.click(screen.getByText('Raipur'));
        expect(handleSelect).toHaveBeenCalledWith(mockLocations[0]);
    });

    it('highlights the selected location', () => {
        render(
            <LocationFeed
                locations={mockLocations}
                onSelect={vi.fn()}
                selectedId="raipur"
            />
        );

        const raipurItem = screen.getByText('Raipur').closest('button');
        expect(raipurItem).toHaveClass('bg-indigo-500/20'); // Expecting Indigo theme highlight
    });
});
