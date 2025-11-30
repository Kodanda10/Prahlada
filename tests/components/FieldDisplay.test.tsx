import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import FieldDisplay from '../../components/FieldDisplay';
import { loadRealTweets } from '../../utils/testDataLoader';

describe('FieldDisplay Component', () => {
  // Load real data
  const realTweets = loadRealTweets();
  
  // Find a tweet with target groups
  const tweetWithTargets = realTweets.find(t => t.parsed_data_v8.target_groups && t.parsed_data_v8.target_groups.length > 0);
  // Fallback to first tweet if none found, but we expect some.
  // If none found, we might need to adjust expectation or acknowledge data quality.
  const testTweet = tweetWithTargets || realTweets[0];
  
  if (!testTweet) throw new Error("No tweets loaded");

  const v8Data = testTweet.parsed_data_v8;

  it('renders label correctly', () => {
    render(<FieldDisplay label="Test Label" values={['Value 1']} color="amber" />);
    expect(screen.getByText('Test Label')).toBeDefined();
  });

  it('renders values from real data (Event Type)', () => {
    // event_type is a string, but FieldDisplay expects string[]
    const eventType = v8Data.event_type || 'Unknown';
    const values = [eventType];

    render(<FieldDisplay label="Event Type" values={values} color="purple" />);
    expect(screen.getByText(eventType)).toBeDefined();
  });

  it('renders array values from real data (Target Groups or Communities)', () => {
    // If target_groups is empty in real data, let's try communities or ensure we handle empty
    // For this test to be meaningful about "rendering array", we prefer an array with items.
    const targets = v8Data.target_groups.length > 0 ? v8Data.target_groups : v8Data.communities;
    
    if (targets.length > 0) {
        render(<FieldDisplay label="Groups" values={targets} color="pink" />);
        targets.forEach(target => {
            expect(screen.getByText(target)).toBeDefined();
        });
    } else {
        // If still empty, verify empty state
        render(<FieldDisplay label="Groups" values={[]} color="pink" />);
        expect(screen.getByText('कोई डेटा नहीं')).toBeDefined();
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
