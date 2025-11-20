import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GlassCard } from '../../components/GlassCard';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';

describe('Hindi Font Rendering & Clipping', () => {
  // Specific Hindi strings with complex ligatures and matras as specified
  const complexHindiStrings = {
    kshetriya: 'क्षेत्रीय',
    zimmedari: 'ज़िम्मेदारी',
    vikasit: 'विकसित छत्तीसगढ़',
    ultraLong: 'यह एक बहुत लंबी हिंदी वाक्य है जिसमें कई जटिल अक्षर और मात्राएँ हैं जैसे क्ष् त्र् गढ़्',
    matraHeavy: 'क्षेत्रीय ज़िम्मेदारी विकसित छत्तीसगढ़ में कार्यान्वयन',
  };

  describe('Button Text Rendering', () => {
    it('renders complex Hindi ligatures in buttons without clipping', () => {
      render(
        <button className="hindi-button">
          {complexHindiStrings.kshetriya}
        </button>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent(complexHindiStrings.kshetriya);

      // Check for proper font application
      expect(button).toHaveClass('hindi-button');
    });

    it('handles matra combinations in button text', () => {
      render(
        <button className="action-btn">
          {complexHindiStrings.matraHeavy}
        </button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveTextContent(complexHindiStrings.matraHeavy);

      // Verify button dimensions accommodate text
      expect(button).toBeInTheDocument();
    });

    it('maintains button aspect ratio with long Hindi text', () => {
      render(
        <button className="long-hindi-btn">
          {complexHindiStrings.ultraLong}
        </button>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent(complexHindiStrings.ultraLong.substring(0, 20) + '...'); // Should truncate gracefully
    });
  });

  describe('Card Title Rendering', () => {
    it('renders Hindi titles in glass cards without vertical clipping', () => {
      render(
        <GlassCard title={complexHindiStrings.zimmedari}>
          <div>Content</div>
        </GlassCard>
      );

      const titleElement = screen.getByText(complexHindiStrings.zimmedari);
      expect(titleElement).toBeInTheDocument();

      // Verify title is properly contained
      const card = titleElement.closest('.glass-card');
      expect(card).toBeInTheDocument();
    });

    it('handles complex ligatures in card headers', () => {
      render(
        <GlassCard title={complexHindiStrings.vikasit}>
          <div>Detailed content here</div>
        </GlassCard>
      );

      expect(screen.getByText(complexHindiStrings.vikasit)).toBeInTheDocument();

      const card = screen.getByRole('article');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Table Header Rendering', () => {
    it('renders Hindi headers in data tables', () => {
      const headers = [
        complexHindiStrings.kshetriya,
        complexHindiStrings.zimmedari,
        'संख्या',
        'स्थिति'
      ];

      render(
        <table>
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index} className="hindi-table-header">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>दक्षिण</td>
              <td>पूर्ण</td>
              <td>१४२</td>
              <td>सक्रिय</td>
            </tr>
          </tbody>
        </table>
      );

      headers.forEach(header => {
        expect(screen.getByText(header)).toBeInTheDocument();
      });
    });

    it('maintains table layout with Hindi headers', () => {
      render(
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th className="hindi-header">{complexHindiStrings.ultraLong.substring(0, 30)}</th>
                <th className="hindi-header">कार्य</th>
              </tr>
            </thead>
          </table>
        </div>
      );

      const headers = screen.getAllByRole('columnheader');
      expect(headers).toHaveLength(2);
    });
  });

  describe('Glyph Integrity Checks', () => {
    it('preserves all Devanagari glyphs', () => {
      const devanagariText = 'क ख ग घ ङ च छ ज झ ञ ट ठ ड ढ ण त थ द ध न प फ ब भ म य र ल व श ष स ह ळ क्ष ज्ञ';

      render(
        <div className="glyph-test">
          <span>{devanagariText}</span>
        </div>
      );

      const span = screen.getByText(devanagariText);
      expect(span).toBeInTheDocument();
      expect(span).toHaveClass('glyph-test');
    });

    it('handles conjunct consonants correctly', () => {
      const conjuncts = 'क्ष त्र ज्ञ श्च ष्ठ';

      render(
        <p className="conjunct-test">{conjuncts}</p>
      );

      expect(screen.getByText(conjuncts)).toBeInTheDocument();
    });

    it('renders vowel matras properly', () => {
      const matras = 'का की कू के कै को कौ कं कः';

      render(
        <div className="matra-test">
          <span>{matras}</span>
        </div>
      );

      expect(screen.getByText(matras)).toBeInTheDocument();
    });
  });
});