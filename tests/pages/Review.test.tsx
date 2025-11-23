import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Review from '../../pages/Review';
import { GeocodingService } from '../../services/GeocodingService';

// Mock GeocodingService
vi.mock('../../services/GeocodingService', () => ({
  GeocodingService: {
    geocode: vi.fn().mockResolvedValue(null),
    getLocationString: vi.fn().mockReturnValue('Test Location')
  }
}));

describe('Review Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads and displays pending tweets', async () => {
    render(<Review />);
    
    // Should show loading initially
    expect(screen.getByText('डेटा लोड हो रहा है...')).toBeDefined();

    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText('डेटा लोड हो रहा है...')).toBeNull();
    });

    // Should show the review card
    expect(screen.getByText(/समीक्षा कतार/)).toBeDefined();
    expect(screen.getByText(/AI समीक्षा सहायक/)).toBeDefined();
  });

  it('approves tweet and moves to next', async () => {
    render(<Review />);

    await waitFor(() => {
      expect(screen.queryByText('डेटा लोड हो रहा है...')).toBeNull();
    });

    // Find approve button
    const approveBtn = screen.getByText('स्वीकृत करें');
    fireEvent.click(approveBtn);

    // Should show success toast
    await waitFor(() => {
      expect(screen.getByText('सुधार सुरक्षित — इस उदाहरण को सीखने के लिए जोड़ दिया गया।')).toBeDefined();
    });
  });
});
