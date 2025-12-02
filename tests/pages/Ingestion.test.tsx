import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Ingestion from '../../pages/Ingestion';

describe('Ingestion Page', () => {
    it('renders without crashing', () => {
        const { container } = render(<BrowserRouter><Ingestion /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
