import { describe, it, expect, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ConfigProvider } from '../../contexts/ConfigContext';
import Assistant from '../../pages/Assistant';

describe('Assistant Page', () => {
    beforeEach(() => {
        // Mock scrollIntoView which is not available in test environment
        Element.prototype.scrollIntoView = () => { };
    });

    it('renders without crashing', () => {
        const { container } = render(
            <BrowserRouter>
                <AuthProvider>
                    <ConfigProvider>
                        <Assistant />
                    </ConfigProvider>
                </AuthProvider>
            </BrowserRouter>
        );
        expect(container).toBeInTheDocument();
    });
});
