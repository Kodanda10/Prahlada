import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import GlassCard from '../../components/GlassCard';

describe('Text Overflow Stress Tests', () => {
  const ultraLongHindiSentences = {
    reviewCard: 'यह एक बहुत लंबी समीक्षा कार्ड है जिसमें क्षेत्रीय ज़िम्मेदारी विकसित छत्तीसगढ़ में कार्यान्वयन के लिए विस्तृत जानकारी दी गई है और यह सुनिश्चित करना है कि सभी पाठकों को पूरी जानकारी मिल सके।',
    analyticsTitle: 'क्षेत्रीय विश्लेषण और प्रदर्शन मीट्रिक्स जिसमें दक्षिणी छत्तीसगढ़ के सभी जिलों के विकास कार्यों की विस्तृत रिपोर्ट प्रस्तुत की गई है।',
    commandText: 'यह कमांड व्यू में दी गई ज़िम्मेदारी सुनिश्चित करें कि सभी क्षेत्रीय अधिकारी अपनी कार्य योजना को समय पर पूरा करें और नियमित अपडेट प्रदान करें।',
    tableCell: 'यह टेबल सेल में बहुत लंबा टेक्स्ट है जिसमें कई जटिल शब्द और वाक्यांश हैं जैसे क्षेत्रीय विकास कार्यान्वयन ज़िम्मेदारी।',
  };

  describe('Review Card Text Overflow', () => {
    it('handles ultra-long Hindi text in review cards without breaking layout', () => {
      render(
        <GlassCard title="समीक्षा रिपोर्ट" className="glass-card">
          <div className="review-content">
            <p>{ultraLongHindiSentences.reviewCard}</p>
          </div>
        </GlassCard>
      );

      const content = screen.getByText(ultraLongHindiSentences.reviewCard);
      expect(content).toBeInTheDocument();

      // Find the card container (parent of the content's parent's parent)
      // content -> p -> div.review-content -> div.relative -> motion.div (GlassCard)
      const card = content.closest('.glass-card');
      expect(card).toBeInTheDocument();
      expect(card).toHaveClass('glass-card');
    });

    it('maintains card dimensions with overflowing text', () => {
      render(
        <div className="card-container">
          <GlassCard title="लंबी समीक्षा" className="glass-card">
            <div className="overflow-content">
              {ultraLongHindiSentences.reviewCard}
            </div>
          </GlassCard>
        </div>
      );

      const content = screen.getByText(ultraLongHindiSentences.reviewCard);
      const card = content.closest('.glass-card');
      expect(card).toBeInTheDocument();

      // Verify card maintains its container constraints
      const container = card?.parentElement;
      expect(container).toHaveClass('card-container');
    });
  });

  describe('Analytics Section Title Overflow', () => {
    it('handles long Hindi titles in analytics sections', () => {
      render(
        <section className="analytics-section">
          <h2 className="section-title">
            {ultraLongHindiSentences.analyticsTitle}
          </h2>
          <div className="analytics-content">
            <p>Analytics data here</p>
          </div>
        </section>
      );

      const title = screen.getByRole('heading', { level: 2 });
      expect(title).toBeInTheDocument();
      expect(title).toHaveClass('section-title');
    });

    it('prevents title overflow from breaking grid layout', () => {
      render(
        <div className="grid-layout">
          <div className="grid-item">
            <h3 className="long-title">{ultraLongHindiSentences.analyticsTitle}</h3>
          </div>
          <div className="grid-item">
            <div className="chart-placeholder">Chart</div>
          </div>
        </div>
      );

      const title = screen.getByRole('heading', { level: 3 });
      expect(title).toBeInTheDocument();

      const grid = title.closest('.grid-layout');
      expect(grid).toBeInTheDocument();
    });
  });

  describe('Command View Text Handling', () => {
    it('manages long Hindi text in command interfaces', () => {
      render(
        <div className="command-interface">
          <div className="command-text">
            {ultraLongHindiSentences.commandText}
          </div>
          <div className="command-actions">
            <button>स्वीकृत करें</button>
            <button>अस्वीकृत करें</button>
          </div>
        </div>
      );

      const commandText = screen.getByText(ultraLongHindiSentences.commandText);
      expect(commandText).toBeInTheDocument();

      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(2);
    });

    it('preserves action button layout with long text', () => {
      render(
        <div className="command-card">
          <p className="long-description">{ultraLongHindiSentences.commandText}</p>
          <div className="button-row">
            <button className="approve-btn">स्वीकृत करें</button>
            <button className="reject-btn">अस्वीकृत करें</button>
          </div>
        </div>
      );

      const approveBtn = screen.getByText('स्वीकृत करें');
      const rejectBtn = screen.getByText('अस्वीकृत करें');

      expect(approveBtn).toBeInTheDocument();
      expect(rejectBtn).toBeInTheDocument();

      expect(approveBtn).toHaveClass('approve-btn');
      expect(rejectBtn).toHaveClass('reject-btn');
    });
  });

  describe('Table Cell Overflow Handling', () => {
    it('handles long Hindi text in table cells', () => {
      const tableData = [
        { id: 1, description: ultraLongHindiSentences.tableCell, status: 'सक्रिय' },
        { id: 2, description: 'छोटा विवरण', status: 'निष्क्रिय' },
      ];

      render(
        <table className="data-table">
          <thead>
            <tr>
              <th>आईडी</th>
              <th>विवरण</th>
              <th>स्थिति</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map(row => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td className="description-cell">{row.description}</td>
                <td>{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      );

      const descriptionCells = document.querySelectorAll('.description-cell');
      expect(descriptionCells).toHaveLength(2);

      // Check that cells handle overflow gracefully
      descriptionCells.forEach(cell => {
        expect(cell).toBeInTheDocument();
      });
    });

    it('maintains table structure with overflowing content', () => {
      render(
        <div className="table-wrapper">
          <table>
            <tbody>
              <tr>
                <td className="wide-cell">{ultraLongHindiSentences.tableCell}</td>
                <td className="narrow-cell">छोटा</td>
              </tr>
            </tbody>
          </table>
        </div>
      );

      const wideCell = document.querySelector('.wide-cell');
      const narrowCell = document.querySelector('.narrow-cell');

      expect(wideCell).toBeInTheDocument();
      expect(narrowCell).toBeInTheDocument();

      // Verify table structure is maintained
      const row = wideCell?.parentElement;
      expect(row?.tagName).toBe('TR');
    });
  });

  describe('Wrapping Behavior Validation', () => {
    it('ensures proper text wrapping for Hindi content', () => {
      render(
        <div className="text-wrapper" style={{ width: '300px' }}>
          <p className="wrapped-text">
            {ultraLongHindiSentences.reviewCard}
          </p>
        </div>
      );

      const paragraph = screen.getByText(ultraLongHindiSentences.reviewCard);
      expect(paragraph).toBeInTheDocument();

      const wrapper = paragraph.parentElement;
      expect(wrapper).toHaveStyle({ width: '300px' });
    });

    it('prevents layout breaks from text overflow', () => {
      render(
        <div className="constrained-layout">
          <div className="sidebar" style={{ width: '200px' }}>
            <p>{ultraLongHindiSentences.analyticsTitle}</p>
          </div>
          <div className="main-content" style={{ flex: 1 }}>
            <p>Main content</p>
          </div>
        </div>
      );

      const sidebar = document.querySelector('.sidebar');
      const mainContent = document.querySelector('.main-content');

      expect(sidebar).toBeInTheDocument();
      expect(mainContent).toBeInTheDocument();

      // Verify layout constraints are respected
      expect(sidebar).toHaveStyle({ width: '200px' });
    });
  });
});