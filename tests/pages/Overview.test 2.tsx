import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Overview from '../../pages/Overview';

describe('Overview Page', () => {
    it('renders without crashing', () => {
        const { container } = render(<BrowserRouter><Overview /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
