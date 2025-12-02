import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Mindmap from '../../pages/Mindmap';

describe('Mindmap Page', () => {
    it('renders without crashing', () => {
        const { container } = render(<BrowserRouter><Mindmap /></BrowserRouter>);
        expect(container).toBeInTheDocument();
    });
});
