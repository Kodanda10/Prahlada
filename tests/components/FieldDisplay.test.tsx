import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import FieldDisplay from '../../components/FieldDisplay';
import realData from '../../data/ingested_tweets.json';

describe('FieldDisplay Component', () => {
  // Use the first tweet from real data
  const sampleTweet = realData[0];
  const v8Data = sampleTweet.parsed_data_v8;

  it('renders label correctly', () => {
    render(<FieldDisplay label="Test Label" values={['Value 1']} color="amber" />);
    expect(screen.getByText('Test Label')).toBeDefined();
  });

  it('renders values from real data (Event Type)', () => {
    // event_type is a string, but FieldDisplay expects string[]
    // So we wrap it in array or use a field that is array
    const values = [v8Data.event_type];
    
    render(<FieldDisplay label="Event Type" values={values} color="purple" />);
    expect(screen.getByText(v8Data.event_type)).toBeDefined();
  });

  it('renders array values from real data (Target Groups)', () => {
    // Find a tweet that has target_groups
    const tweetWithTargets = realData.find(t => t.parsed_data_v8.target_groups && t.parsed_data_v8.target_groups.length > 0);
    
    if (tweetWithTargets) {
      const targets = tweetWithTargets.parsed_data_v8.target_groups;
      render(<FieldDisplay label="Target Groups" values={targets} color="pink" />);
      
      targets.forEach(target => {
        expect(screen.getByText(target)).toBeDefined();
      });
    } else {
      console.warn('No tweet found with target_groups in sample data');
    }
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
