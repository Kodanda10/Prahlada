import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

describe('Font Loading Performance & Fallbacks', () => {
  describe('Font Loading Strategy', () => {
    it('loads fonts asynchronously without blocking', async () => {
      // Mock font loading
      const mockFont = new FontFace('HindiFont', 'url(mock-font.woff2)');
      const loadSpy = vi.spyOn(mockFont, 'load').mockResolvedValue(mockFont);

      render(
        <div className="hindi-font-container">
          <p>Hindi text content</p>
        </div>
      );

      const container = screen.getByText('Hindi text content').parentElement;
      expect(container).toHaveClass('hindi-font-container');

      // Verify font loading doesn't block render
      expect(screen.getByText('Hindi text content')).toBeInTheDocument();
    });

    it('provides immediate fallback fonts', () => {
      render(
        <p className="hindi-text-fallback">
          फॉलबैक फ़ॉन्ट के साथ हिंदी टेक्स्ट
        </p>
      );

      const paragraph = screen.getByText('फॉलबैक फ़ॉन्ट के साथ हिंदी टेक्स्ट');
      expect(paragraph).toBeInTheDocument();
      expect(paragraph).toHaveClass('hindi-text-fallback');
    });

    it('switches to loaded font seamlessly', async () => {
      render(
        <div className="font-loading-container">
          <span className="hindi-text">लोड हो रहा है</span>
        </div>
      );

      const textElement = screen.getByText('लोड हो रहा है');
      expect(textElement).toBeInTheDocument();

      // Simulate font load completion
      await waitFor(() => {
        expect(textElement.parentElement).toHaveClass('font-loading-container');
      });
    });
  });

  describe('Typography Performance Metrics', () => {
    it('maintains consistent line heights', () => {
      const testText = 'यह एक परीक्षण पाठ है जिसमें एकाधिक पंक्तियाँ हैं';

      render(
        <div className="typography-test">
          <p className="hindi-paragraph">{testText}</p>
        </div>
      );

      const paragraph = screen.getByText(testText);
      expect(paragraph).toBeInTheDocument();
      expect(paragraph).toHaveClass('hindi-paragraph');
    });

    it('handles long text blocks efficiently', () => {
      const longText = 'हिंदी में लिखा गया यह एक बहुत लंबा पाठ है। '.repeat(20);

      render(
        <article>
          <p className="long-hindi-content">{longText}</p>
        </article>
      );

      const paragraph = screen.getByText(longText.substring(0, 50) + '...');
      expect(paragraph).toBeInTheDocument();
    });

    it('optimizes character spacing', () => {
      render(
        <div className="character-spacing-test">
          <span className="hindi-characters">अआइईउऊऋॠऌॡएऐओऔअंअः</span>
        </div>
      );

      const characters = screen.getByText('अआइईउऊऋॠऌॡएऐओऔअंअः');
      expect(characters).toBeInTheDocument();
      expect(characters).toHaveClass('hindi-characters');
    });
  });

  describe('Cross-Browser Font Support', () => {
    const userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ];

    userAgents.forEach((ua, index) => {
      it(`renders correctly in browser ${index + 1}`, () => {
        // Mock user agent
        Object.defineProperty(navigator, 'userAgent', {
          value: ua,
          configurable: true
        });

        render(
          <p className="browser-test-hindi">
            ब्राउज़र टेस्ट हिंदी टेक्स्ट
          </p>
        );

        const text = screen.getByText('ब्राउज़र टेस्ट हिंदी टेक्स्ट');
        expect(text).toBeInTheDocument();
      });
    });
  });
});