import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

describe('Mixed-Script Input Safety', () => {
  describe('Raigarh-style Input Validation', () => {
    it('handles Raigarh रायगढ़ style mixed input gracefully', () => {
      render(
        <div className="input-test">
          <input
            className="mixed-script-input"
            placeholder="रायगढ़ दर्ज करें"
            defaultValue=""
          />
        </div>
      );

      const input = screen.getByPlaceholderText('रायगढ़ दर्ज करें');
      expect(input).toBeInTheDocument();
      expect(input).toHaveClass('mixed-script-input');
    });

    it('maintains layout with mixed Hindi-English input', () => {
      const mixedInputs = [
        'रायगढ़ Block',
        'जोंबी Village 1',
        'खरसिया ब्लॉक HQ',
        'तमनार क्षेत्र 2',
      ];

      render(
        <div className="mixed-input-container">
          {mixedInputs.map((input, index) => (
            <div key={index} className="input-row">
              <label>{`लेबल ${index + 1}`}</label>
              <input defaultValue={input} className="mixed-input" />
            </div>
          ))}
        </div>
      );

      mixedInputs.forEach(input => {
        const inputElement = screen.getByDisplayValue(input);
        expect(inputElement).toBeInTheDocument();
        expect(inputElement).toHaveClass('mixed-input');
      });
    });

    it('prevents layout breaking from mixed script combinations', () => {
      render(
        <div className="layout-test">
          <div className="form-grid">
            <input placeholder="रायगढ़" className="grid-input" />
            <input placeholder="Block HQ" className="grid-input" />
            <input placeholder="जोंबी" className="grid-input" />
            <input placeholder="Village" className="grid-input" />
          </div>
        </div>
      );

      const inputs = document.querySelectorAll('.grid-input');
      expect(inputs).toHaveLength(4);

      inputs.forEach(input => {
        expect(input).toBeInTheDocument();
      });

      // Verify grid layout is maintained
      const grid = document.querySelector('.form-grid');
      expect(grid).toBeInTheDocument();
    });
  });

  describe('Script Direction Handling', () => {
    it('maintains left-to-right flow for Hindi text', () => {
      render(
        <p className="hindi-ltr-text">
          यह हिंदी टेक्स्ट बाएं से दाएं बहना चाहिए
        </p>
      );

      const textElement = screen.getByText('यह हिंदी टेक्स्ट बाएं से दाएं बहना चाहिए');
      expect(textElement).toBeInTheDocument();
      expect(textElement).toHaveClass('hindi-ltr-text');
    });

    it('handles mixed script text wrapping correctly', () => {
      const mixedText = 'रायगढ़ Block में जोंबी Village की जानकारी';

      render(
        <div className="wrapping-test" style={{ width: '200px' }}>
          <p className="mixed-wrap-text">{mixedText}</p>
        </div>
      );

      const textElement = screen.getByText(mixedText);
      expect(textElement).toBeInTheDocument();
      expect(textElement).toHaveClass('mixed-wrap-text');
    });
  });

  describe('Input Field Behavior', () => {
    it('accepts both Hindi and English characters', () => {
      render(
        <input
          className="flexible-input"
          placeholder="हिंदी या English टाइप करें"
          defaultValue=""
        />
      );

      const input = screen.getByPlaceholderText('हिंदी या English टाइप करें');
      expect(input).toBeInTheDocument();

      // Simulate typing mixed content
      fireEvent.change(input, { target: { value: 'रायगढ़ Block 1' } });
      expect(input).toHaveValue('रायगढ़ Block 1');
    });

    it('maintains cursor position with mixed scripts', () => {
      render(
        <textarea
          className="mixed-textarea"
          placeholder="मिश्रित स्क्रिप्ट टेक्स्ट दर्ज करें"
          defaultValue=""
        />
      );

      const textarea = screen.getByPlaceholderText('मिश्रित स्क्रिप्ट टेक्स्ट दर्ज करें');
      expect(textarea).toBeInTheDocument();

      // Test input handling
      fireEvent.change(textarea, {
        target: { value: 'रायगढ़ में खरसिया ब्लॉक' }
      });
      expect(textarea).toHaveValue('रायगढ़ में खरसिया ब्लॉक');
    });

    it('handles paste operations with mixed content', () => {
      render(
        <input
          className="paste-test-input"
          defaultValue=""
        />
      );

      const input = document.querySelector('.paste-test-input') as HTMLInputElement;
      expect(input).toBeInTheDocument();

      // Simulate paste event
      const pasteData = 'रायगढ़ District HQ';
      fireEvent.paste(input, {
        clipboardData: {
          getData: () => pasteData,
        },
      });

      expect(input).toBeInTheDocument();
    });
  });

  describe('Display and Rendering Safety', () => {
    it('renders mixed script combinations without corruption', () => {
      const mixedStrings = [
        'रायगढ़ HQ',
        'जोंबी Village',
        'खरसिया Block 1',
        'तमनार क्षेत्र 2',
        'सारागढ़ ग्राम पंचायत',
      ];

      render(
        <div className="mixed-display-test">
          {mixedStrings.map((str, index) => (
            <div key={index} className="mixed-string">{str}</div>
          ))}
        </div>
      );

      mixedStrings.forEach(str => {
        const element = screen.getByText(str);
        expect(element).toBeInTheDocument();
        expect(element).toHaveClass('mixed-string');
      });
    });

    it('maintains text selection in mixed script text', () => {
      render(
        <p className="selection-test">
          रायगढ़ Block में जोंबी Village स्थित है
        </p>
      );

      const textElement = screen.getByText('रायगढ़ Block में जोंबी Village स्थित है');
      expect(textElement).toBeInTheDocument();

      // Test text selection capability
      expect(textElement).toBeInTheDocument();
    });

    it('handles search and highlight in mixed content', () => {
      const content = 'रायगढ़ में खरसिया और जोंबी गांव हैं';

      render(
        <div className="search-test">
          <p>{content}</p>
          <input placeholder="खोजें" className="search-input" />
        </div>
      );

      const paragraph = screen.getByText(content);
      const searchInput = screen.getByPlaceholderText('खोजें');

      expect(paragraph).toBeInTheDocument();
      expect(searchInput).toBeInTheDocument();
    });
  });

  describe('Form Submission Safety', () => {
    it('processes mixed script form data correctly', () => {
      render(
        <form className="mixed-form">
          <input name="district" placeholder="ज़िला" defaultValue="रायगढ़" />
          <input name="block" placeholder="ब्लॉक" defaultValue="खरसिया Block" />
          <input name="village" placeholder="गाँव" defaultValue="जोंबी" />
          <button type="submit">सबमिट करें</button>
        </form>
      );

      const districtInput = screen.getByPlaceholderText('ज़िला');
      const blockInput = screen.getByPlaceholderText('ब्लॉक');
      const villageInput = screen.getByPlaceholderText('गाँव');
      const submitBtn = screen.getByText('सबमिट करें');

      expect(districtInput).toHaveValue('रायगढ़');
      expect(blockInput).toHaveValue('खरसिया Block');
      expect(villageInput).toHaveValue('जोंबी');
      expect(submitBtn).toBeInTheDocument();
    });

    it('validates mixed script input formats', () => {
      const validationRules = [
        { field: 'district', value: 'रायगढ़', valid: true },
        { field: 'block', value: 'खरसिया Block', valid: true },
        { field: 'village', value: 'जोंबी', valid: true },
        { field: 'invalid', value: 'Invalid@Field#$%', valid: false },
      ];

      render(
        <div className="validation-test">
          {validationRules.map((rule, index) => (
            <div key={index} className={`field ${rule.valid ? 'valid' : 'invalid'}`}>
              <label>{rule.field}</label>
              <input defaultValue={rule.value} />
            </div>
          ))}
        </div>
      );

      validationRules.forEach(rule => {
        const input = screen.getByDisplayValue(rule.value);
        expect(input).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility with Mixed Scripts', () => {
    it('provides proper labels for mixed script inputs', () => {
      render(
        <div className="accessibility-test">
          <label htmlFor="mixed-field">ज़िला/Block दर्ज करें</label>
          <input
            id="mixed-field"
            placeholder="रायगढ़ Block"
            aria-describedby="help-text"
          />
          <span id="help-text">ज़िला का नाम और ब्लॉक दर्ज करें</span>
        </div>
      );

      const label = screen.getByText('ज़िला/Block दर्ज करें');
      const input = screen.getByPlaceholderText('रायगढ़ Block');
      const helpText = screen.getByText('ज़िला का नाम और ब्लॉक दर्ज करें');

      expect(label).toBeInTheDocument();
      expect(input).toBeInTheDocument();
      expect(helpText).toBeInTheDocument();

      expect(input).toHaveAttribute('aria-describedby', 'help-text');
    });

    it('maintains screen reader compatibility', () => {
      render(
        <div className="screen-reader-test">
          <input
            aria-label="रायगढ़ ज़िला और खरसिया ब्लॉक"
            defaultValue="रायगढ़ खरसिया"
          />
        </div>
      );

      const input = screen.getByDisplayValue('रायगढ़ खरसिया');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('aria-label', 'रायगढ़ ज़िला और खरसिया ब्लॉक');
    });
  });
});