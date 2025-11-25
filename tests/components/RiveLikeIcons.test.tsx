import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PulseButton, LiquidLoader } from '../../components/interactions/RiveLikeIcons';

describe('RiveLikeIcons', () => {
  describe('PulseButton', () => {
    it('renders with default label', () => {
      const onClick = vi.fn();
      render(<PulseButton onClick={onClick} />);
      expect(screen.getByText('रिफ्रेश')).toBeInTheDocument();
    });

    it('renders with custom label', () => {
      const onClick = vi.fn();
      render(<PulseButton onClick={onClick} label="कस्टम" />);
      expect(screen.getByText('कस्टम')).toBeInTheDocument();
    });

    it('calls onClick when clicked', () => {
      const onClick = vi.fn();
      render(<PulseButton onClick={onClick} />);
      fireEvent.click(screen.getByText('रिफ्रेश'));
      expect(onClick).toHaveBeenCalled();
    });

    it('shows loading state', () => {
      const onClick = vi.fn();
      const { container } = render(<PulseButton onClick={onClick} isLoading={true} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('LiquidLoader', () => {
    it('renders loading text', () => {
      render(<LiquidLoader />);
      expect(screen.getByText('डेटा लोड हो रहा है...')).toBeInTheDocument();
    });

    it('renders loader animation', () => {
      const { container } = render(<LiquidLoader />);
      expect(container.querySelector('.rounded-full')).toBeInTheDocument();
    });
  });
});
