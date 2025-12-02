import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from '../../contexts/ConfigContext';
import ControlHub from '../../pages/ControlHub';

describe('ControlHub Page', () => {
    it('renders without crashing', () => {
        const { container } = render(
            <BrowserRouter>
                <ConfigProvider>
                    <ControlHub />
                </ConfigProvider>
            </BrowserRouter>
        );
        expect(container).toBeInTheDocument();
    });
});
