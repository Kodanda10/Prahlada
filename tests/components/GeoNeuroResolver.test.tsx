import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GeoNeuroResolver from '../../src/components/decision/GeoNeuroResolver';
import { BoundaryService } from '../../services/BoundaryService';

// Mock BoundaryService
vi.mock('../../services/BoundaryService', () => ({
  BoundaryService: {
    loadHierarchyData: vi.fn(),
  },
}));

// Mock fetch for Hindi data
global.fetch = vi.fn();

const mockHierarchy = {
  "Raipur": {
    "Raipur North": {
      "Raipur": [{ name: "Raipur", code: "123" }]
    }
  }
};

const mockHindiHierarchy = {
  "Raipur": {
    "name_hi": "रायपुर",
    "acs": {
      "Raipur North": {
        "name_hi": "रायपुर उत्तर",
        "blocks": {
          "Raipur": {
            "name_hi": "रायपुर",
            "villages": [{ name: "Raipur", name_hi: "रायपुर", code: "123" }]
          }
        }
      }
    }
  }
};

describe('GeoNeuroResolver', () => {
  const mockOnClose = vi.fn();
  const mockOnSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (BoundaryService.loadHierarchyData as any).mockResolvedValue(mockHierarchy);
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockHindiHierarchy,
    });
  });

  it('renders correctly when open', async () => {
    render(
      <GeoNeuroResolver
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByText('स्थान चयन')).toBeInTheDocument();
    expect(screen.getByText('ग्रामीण')).toBeInTheDocument();
    expect(screen.getByText('शहरी')).toBeInTheDocument();
  });

  it('loads and displays Hindi names', async () => {
    render(
      <GeoNeuroResolver
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('रायपुर')).toBeInTheDocument();
    });
  });

  it('switches area type and theme', async () => {
    render(
      <GeoNeuroResolver
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />
    );

    const urbanChip = screen.getByText('शहरी');
    fireEvent.click(urbanChip);

    // Check if urban specific elements or classes are applied
    // Note: Testing CSS classes directly might be tricky depending on how they are applied,
    // but we can check if the state changed by looking for Urban specific steps if any
    // For now, just verifying the click doesn't crash
    expect(screen.getByText('शहरी')).toBeInTheDocument();
  });

  it('filters items based on search', async () => {
    render(
      <GeoNeuroResolver
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('रायपुर')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('स्थान खोजें...');
    fireEvent.change(searchInput, { target: { value: 'xyz' } });

    expect(screen.queryByText('रायपुर')).not.toBeInTheDocument();
    expect(screen.getByText(/"xyz" से मेल खाता कोई स्थान नहीं मिला/)).toBeInTheDocument();
  });
});
