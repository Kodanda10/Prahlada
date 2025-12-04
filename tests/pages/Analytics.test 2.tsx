import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Analytics from '../../pages/Analytics';

describe('Analytics Page', () => {
    it('renders without crashing', () => {
        const { container } = render(<BrowserRouter><Analytics /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
