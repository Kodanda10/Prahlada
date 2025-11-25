import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';

interface LocationData {
    id: string;
    lat: number;
    lng: number;
    label: string;
    type: 'urban' | 'rural' | 'unknown';
    hierarchy_path: string[];
    visit_count: number;
    event_type?: string;
    date?: string;
}

describe('MapBoxVisual Component', () => {
    const mockLocations: LocationData[] = [
        {
            id: '1',
            lat: 21.25,
            lng: 82.15,
            label: 'रायगढ़',
            type: 'urban',
            hierarchy_path: ['छत्तीसगढ़', 'रायगढ़'],
            visit_count: 142,
            event_type: 'सभा'
        },
        {
            id: '2',
            lat: 21.30,
            lng: 82.20,
            label: 'खरसिया',
            type: 'rural',
            hierarchy_path: ['छत्तीसगढ़', 'रायगढ़', 'खरसिया'],
            visit_count: 78
        }
    ];

    it('renders the map container', () => {
        const { container } = render(<MapBoxVisual locations={mockLocations} />);
        expect(container.firstChild).toBeInTheDocument();
    });

    it('displays loading state', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        expect(screen.getByText(/मानचित्र लोड हो रहा है/)).toBeInTheDocument();
    });

    it('displays district name', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        expect(screen.getByText('रायगढ़ जिला कवरेज')).toBeInTheDocument();
    });

    it('shows legend with Hindi labels', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        expect(screen.getByText('ग्रामीण')).toBeInTheDocument();
        expect(screen.getByText('शहरी')).toBeInTheDocument();
    });

    it('renders map style toggle', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        expect(screen.getByText('Satellite')).toBeInTheDocument();
    });

    it('renders cluster toggle', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        const clusterButton = screen.getByText('Cluster');
        expect(clusterButton).toBeInTheDocument();
        expect(clusterButton).toHaveClass('bg-[#8BF5E6]');
    });

    it('toggles map style on click', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        const styleButton = screen.getByText('Satellite');
        fireEvent.click(styleButton);
        expect(screen.getByText('Dark')).toBeInTheDocument();
    });

    it('renders fullscreen button', () => {
        render(<MapBoxVisual locations={mockLocations} />);
        expect(screen.getByTitle(/Fullscreen/)).toBeInTheDocument();
    });

    it('renders with empty locations', () => {
        const { container } = render(<MapBoxVisual locations={[]} />);
        expect(container.firstChild).toBeInTheDocument();
    });

    it('accepts custom API key', () => {
        const { container } = render(<MapBoxVisual locations={mockLocations} apiKey="test-key" />);
        expect(container.firstChild).toBeInTheDocument();
    });

    it('applies proper styling classes', () => {
        const { container } = render(<MapBoxVisual locations={mockLocations} />);
        const mapContainer = container.firstChild as HTMLElement;
        expect(mapContainer).toHaveClass('relative');
        expect(mapContainer).toHaveClass('border');
    });
});
