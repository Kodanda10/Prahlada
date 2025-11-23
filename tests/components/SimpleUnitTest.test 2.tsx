import { describe, it, expect } from 'vitest';

describe('Simple Unit Test', () => {
  it('basic math works', () => {
    expect(2 + 2).toBe(4);
  });

  it('string operations work', () => {
    expect('hello'.toUpperCase()).toBe('HELLO');
  });
});
