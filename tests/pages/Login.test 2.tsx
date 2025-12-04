import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Login from '../../pages/Login';

describe('Login Page', () => {
    it('renders without crashing', () => {
        const { container } = render(
            <BrowserRouter>
                <AuthProvider>
                    <Login />
                </AuthProvider>
            </BrowserRouter>
        );
        expect(container).toBeInTheDocument();
    });
});
