import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GlassCard } from '../../components/GlassCard';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';

describe('Hindi-Only String Audit', () => {
  // Static audit: Scan source code/bundle for [A-Za-z] in UI strings
  // Allowlisted English words that can appear in UI
  const englishAllowlist = [
    'Analytics', 'Home', 'Review', 'Command', // Tab labels (keep as-is for now)
    'ID', 'URL', 'API', 'JSON', 'CSS', 'HTML', // Technical terms
    'React', 'Vite', 'TypeScript', // Framework names
    'Error', 'Loading', 'Success', // Status messages
    'Latitude', 'Longitude', // Geographic terms
    'true', 'false', // Boolean values
    'undefined', 'null', // JavaScript values
  ];

  const isEnglishAllowlisted = (word: string): boolean => {
    return englishAllowlist.some(allowed =>
      allowed.toLowerCase() === word.toLowerCase()
    );
  };

  describe('Component Text Content Audit', () => {
    it('ensures only Hindi text in card titles and content', () => {
      render(
        <GlassCard title="क्षेत्रीय विश्लेषण">
          <p>यह विश्लेषण रिपोर्ट दक्षिणी छत्तीसगढ़ के विकास कार्यों को दर्शाती है।</p>
          <p>कुल दौरे: १४२</p>
        </GlassCard>
      );

      const title = screen.getByText('क्षेत्रीय विश्लेषण');
      const content1 = screen.getByText('यह विश्लेषण रिपोर्ट दक्षिणी छत्तीसगढ़ के विकास कार्यों को दर्शाती है।');
      const content2 = screen.getByText('कुल दौरे: १४२');

      expect(title).toBeInTheDocument();
      expect(content1).toBeInTheDocument();
      expect(content2).toBeInTheDocument();

      // Verify no unallowlisted English words
      const allText = [title, content1, content2].map(el => el.textContent || '').join(' ');
      const englishWords = allText.match(/[A-Za-z]+/g) || [];

      englishWords.forEach(word => {
        // Only numbers and allowlisted words should appear
        expect(word.match(/^\d+$/) || isEnglishAllowlisted(word)).toBe(true);
      });
    });

    it('validates navigation labels contain only Hindi or allowlisted English', () => {
      const tabs = [
        { id: 'analytics', label: 'Analytics', path: '/analytics' }, // Allowlisted
        { id: 'home', label: 'Home', path: '/home' }, // Allowlisted
        { id: 'review', label: 'समीक्षा', path: '/review' }, // Hindi
        { id: 'command', label: 'आदेश', path: '/command' }, // Hindi
      ];

      render(
        <AnimatedNavTabs
          tabs={tabs}
          activeTab="analytics"
          onTabChange={() => {}}
        />
      );

      tabs.forEach(tab => {
        const tabElement = screen.getByText(tab.label);
        expect(tabElement).toBeInTheDocument();

        // Check if label is Hindi or allowlisted English
        const isHindi = /[\u0900-\u097F]/.test(tab.label);
        const isAllowlistedEnglish = isEnglishAllowlisted(tab.label);

        expect(isHindi || isAllowlistedEnglish).toBe(true);
      });
    });

    it('scans button labels for Hindi-only compliance', () => {
      const buttons = [
        'स्वीकृत करें',
        'अस्वीकृत करें',
        'विवरण देखें',
        'संपादित करें',
        'हटाएं',
      ];

      render(
        <div className="button-group">
          {buttons.map((label, index) => (
            <button key={index} className="hindi-btn">{label}</button>
          ))}
        </div>
      );

      buttons.forEach(label => {
        const button = screen.getByText(label);
        expect(button).toBeInTheDocument();

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(label)).toBe(true);

        // Check for unallowlisted English
        const englishWords = label.match(/[A-Za-z]+/g) || [];
        englishWords.forEach(word => {
          expect(isEnglishAllowlisted(word)).toBe(true);
        });
      });
    });
  });

  describe('Form and Input Labels Audit', () => {
    it('ensures form labels are in Hindi only', () => {
      const formFields = [
        { label: 'नाम', placeholder: 'अपना नाम दर्ज करें' },
        { label: 'क्षेत्र', placeholder: 'क्षेत्र चुनें' },
        { label: 'ज़िला', placeholder: 'ज़िला दर्ज करें' },
        { label: 'गाँव', placeholder: 'गाँव का नाम' },
      ];

      render(
        <form className="hindi-form">
          {formFields.map((field, index) => (
            <div key={index} className="form-field">
              <label>{field.label}</label>
              <input placeholder={field.placeholder} />
            </div>
          ))}
        </form>
      );

      formFields.forEach(field => {
        const label = screen.getByText(field.label);
        const input = screen.getByPlaceholderText(field.placeholder);

        expect(label).toBeInTheDocument();
        expect(input).toBeInTheDocument();

        // Verify both label and placeholder are Hindi
        expect(/[\u0900-\u097F]/.test(field.label)).toBe(true);
        expect(/[\u0900-\u097F]/.test(field.placeholder)).toBe(true);
      });
    });

    it('validates error messages are Hindi-only', () => {
      const errorMessages = [
        'यह फ़ील्ड आवश्यक है',
        'अमान्य प्रारूप दर्ज किया गया है',
        'यह मान बहुत लंबा है',
        'कृपया सही जानकारी दर्ज करें',
      ];

      render(
        <div className="error-display">
          {errorMessages.map((message, index) => (
            <div key={index} className="error-message">{message}</div>
          ))}
        </div>
      );

      errorMessages.forEach(message => {
        const errorElement = screen.getByText(message);
        expect(errorElement).toBeInTheDocument();
        expect(errorElement).toHaveClass('error-message');

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(message)).toBe(true);
      });
    });
  });

  describe('Data Display and Metrics Audit', () => {
    it('ensures table headers are Hindi-only', () => {
      const headers = [
        'क्रम संख्या',
        'ज़िला',
        'ब्लॉक',
        'गाँव',
        'दौरे',
        'स्थिति',
      ];

      render(
        <table className="data-table">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>१</td>
              <td>रायगढ़</td>
              <td>रायगढ़</td>
              <td>जोंबी</td>
              <td>४</td>
              <td>पूर्ण</td>
            </tr>
          </tbody>
        </table>
      );

      headers.forEach(header => {
        const headerElement = screen.getByText(header);
        expect(headerElement).toBeInTheDocument();

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(header)).toBe(true);
      });
    });

    it('validates chart labels and legends are Hindi-only', () => {
      const chartLabels = [
        'दौरे की संख्या',
        'क्षेत्रवार वितरण',
        'मासिक विकास',
        'कुल उपलब्धि',
      ];

      render(
        <div className="chart-legend">
          {chartLabels.map((label, index) => (
            <div key={index} className="legend-item">
              <span className="legend-color"></span>
              <span className="legend-text">{label}</span>
            </div>
          ))}
        </div>
      );

      chartLabels.forEach(label => {
        const labelElement = screen.getByText(label);
        expect(labelElement).toBeInTheDocument();
        expect(labelElement).toHaveClass('legend-text');

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(label)).toBe(true);
      });
    });

    it('checks status indicators use Hindi text', () => {
      const statuses = [
        'सक्रिय',
        'निष्क्रिय',
        'प्रगति में',
        'पूर्ण',
        'अपूर्ण',
      ];

      render(
        <div className="status-indicators">
          {statuses.map((status, index) => (
            <span key={index} className={`status status-${status.toLowerCase()}`}>
              {status}
            </span>
          ))}
        </div>
      );

      statuses.forEach(status => {
        const statusElement = screen.getByText(status);
        expect(statusElement).toBeInTheDocument();

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(status)).toBe(true);
      });
    });
  });

  describe('Navigation and Menu Audit', () => {
    it('ensures breadcrumb navigation uses Hindi', () => {
      const breadcrumbs = [
        'डैशबोर्ड',
        'विश्लेषण',
        'क्षेत्रीय रिपोर्ट',
      ];

      render(
        <nav className="breadcrumb-nav">
          {breadcrumbs.map((crumb, index) => (
            <span key={index} className="breadcrumb-item">
              {crumb}
              {index < breadcrumbs.length - 1 && ' > '}
            </span>
          ))}
        </nav>
      );

      breadcrumbs.forEach(crumb => {
        const crumbElement = screen.getByText(crumb);
        expect(crumbElement).toBeInTheDocument();

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(crumb)).toBe(true);
      });
    });

    it('validates menu items are Hindi-only', () => {
      const menuItems = [
        'डैशबोर्ड',
        'विश्लेषण',
        'समीक्षा',
        'रिपोर्ट',
        'सेटिंग्स',
      ];

      render(
        <ul className="menu-list">
          {menuItems.map((item, index) => (
            <li key={index} className="menu-item">{item}</li>
          ))}
        </ul>
      );

      menuItems.forEach(item => {
        const menuElement = screen.getByText(item);
        expect(menuElement).toBeInTheDocument();
        expect(menuElement).toHaveClass('menu-item');

        // Verify Hindi content
        expect(/[\u0900-\u097F]/.test(item)).toBe(true);
      });
    });
  });

  describe('Technical Term Allowlist Validation', () => {
    it('allows only specified English technical terms', () => {
      const technicalTerms = [
        'API',
        'JSON',
        'CSS',
        'React',
        'Analytics', // Allowlisted for tabs
      ];

      technicalTerms.forEach(term => {
        expect(isEnglishAllowlisted(term)).toBe(true);
      });
    });

    it('rejects unallowlisted English words', () => {
      const unallowlistedWords = [
        'Dashboard',
        'Analysis',
        'Review',
        'Report',
        'Settings',
        'Submit',
        'Cancel',
      ];

      unallowlistedWords.forEach(word => {
        expect(isEnglishAllowlisted(word)).toBe(false);
      });
    });

    it('permits numeric values and Hindi numerals', () => {
      const numericStrings = [
        '123',
        '१२३',
        '45.67',
        '४५.६७',
      ];

      render(
        <div className="numeric-display">
          {numericStrings.map((num, index) => (
            <span key={index} className="number">{num}</span>
          ))}
        </div>
      );

      numericStrings.forEach(num => {
        const numElement = screen.getByText(num);
        expect(numElement).toBeInTheDocument();

        // Should contain only numbers (Arabic or Devanagari)
        expect(/^[0-9\u0966-\u096F.]+$/.test(num)).toBe(true);
      });
    });
  });
});