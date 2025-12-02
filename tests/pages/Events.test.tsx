import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Events from '../../pages/Events';

describe('Events Page', () => {
    it('renders without crashing', () => {
        const { container } = render(<BrowserRouter><Events /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
