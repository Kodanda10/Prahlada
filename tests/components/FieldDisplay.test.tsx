import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import FieldDisplay from '../../components/FieldDisplay';

describe('FieldDisplay Component', () => {
  // Mock tweet data for testing
  const mockTweet = {
    parsed_data_v8: {
      event_type: 'सभा',
      target_groups: ['किसान', 'महिलाएं', 'युवा'],
      location: 'रायगढ़',
      date: '2024-01-15'
    }
  };

  const v8Data = mockTweet.parsed_data_v8;

  it('renders label correctly', () => {
    render(<FieldDisplay label="Test Label" values={['Value 1']} color="amber" />);
    expect(screen.getByText('Test Label')).toBeDefined();
  });

  it('renders values from mock data (Event Type)', () => {
    // event_type is a string, but FieldDisplay expects string[]
    // So we wrap it in array
    const values = [v8Data.event_type];

    render(<FieldDisplay label="Event Type" values={values} color="purple" />);
    expect(screen.getByText(v8Data.event_type)).toBeDefined();
  });

  it('renders array values from mock data (Target Groups)', () => {
    const targets = v8Data.target_groups;
    render(<FieldDisplay label="Target Groups" values={targets} color="pink" />);

    targets.forEach(target => {
      expect(screen.getByText(target)).toBeDefined();
    });
  });

  it('shows empty state when values are missing', () => {
    render(<FieldDisplay label="Empty Field" values={[]} color="blue" />);
    expect(screen.getByText('कोई डेटा नहीं')).toBeDefined();
  });

  it('applies correct color class (Amber)', () => {
    const { container } = render(<FieldDisplay label="Color Test" values={['Test']} color="amber" />);
    const badge = screen.getByText('Test');
    expect(badge.className).toContain('text-amber-300');
  });
});
