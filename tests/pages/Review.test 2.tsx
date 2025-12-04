import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Review from '../../pages/Review';

describe('Review Page', () => {
    it('renders without crashing', () => {
        const { container } = render(<BrowserRouter><Review /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
