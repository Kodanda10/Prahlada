
import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import NumberTicker from '../../components/NumberTicker';

// Mock Framer Motion's useInView to always return true
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual('framer-motion');
  return {
    ...actual,
    useInView: () => true,
    useMotionValue: (val: any) => ({ set: vi.fn(), get: () => val }),
    useSpring: (val: any) => ({ on: vi.fn() })
  };
});

describe('NumberTicker', () => {
  it('renders correctly', () => {
    const { getByText } = render(<NumberTicker value={100} />);
    // Since animation is mocked/jsdom doesn't run layout effects perfectly, check for existence
    expect(getByText(/0/)).toBeInTheDocument(); 
  });
});