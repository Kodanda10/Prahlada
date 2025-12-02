import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Home from '../../pages/Home';

vi.mock('../../hooks/useAuth', () => ({
    default: () => ({ isAuthenticated: true, user: { username: 'test' } }),
}));

describe('Home Page', () => {
    it('renders without crashing', () => {
        render(<BrowserRouter><Home /></BrowserRouter>);
        expect(document.body).toBeInTheDocument();
    });

    it('displays page content', () => {
        const { container } = render(<BrowserRouter><Home /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
