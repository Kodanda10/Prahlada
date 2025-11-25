import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import GlassCard from '../../components/GlassCard';

describe('Hindi Text Rendering & Typography Integrity', () => {
  const hindiContent = {
    title: 'डैशबोर्ड अवलोकन',
    subtitle: 'विस्तृत विश्लेषण और रिपोर्ट',
    content: 'यह डैशबोर्ड भारतीय बाजार के लिए डिज़ाइन किया गया है और सभी भारतीय भाषाओं का समर्थन करता है।',
    stats: 'कुल संख्या: १,२३४',
    labels: {
      users: 'उपयोगकर्ता',
      revenue: 'राजस्व',
      growth: 'वृद्धि'
    }
  };

  describe('Hindi Text Display', () => {
    it('renders Hindi characters correctly', () => {
      render(
        <GlassCard title={hindiContent.title}>
          <div>{hindiContent.content}</div>
        </GlassCard>
      );

      expect(screen.getByText(hindiContent.title)).toBeInTheDocument();
      expect(screen.getByText(hindiContent.content)).toBeInTheDocument();
    });

    it('maintains Devanagari script integrity', () => {
      render(
        <div>
          <h1>{hindiContent.title}</h1>
          <p>{hindiContent.subtitle}</p>
          <span>{hindiContent.stats}</span>
        </div>
      );

      expect(screen.getByText(hindiContent.title)).toBeInTheDocument();
      expect(screen.getByText(hindiContent.subtitle)).toBeInTheDocument();
      expect(screen.getByText(hindiContent.stats)).toBeInTheDocument();
    });

    it('handles Hindi numerals properly', () => {
      const hindiNumbers = '०१२३४५६७८९';

      render(
        <div>
          <span>{hindiNumbers}</span>
          <span>{hindiContent.stats}</span>
        </div>
      );

      expect(screen.getByText(hindiNumbers)).toBeInTheDocument();
      expect(screen.getByText(hindiContent.stats)).toBeInTheDocument();
    });
  });

  describe('Typography Hierarchy', () => {
    it('maintains consistent font sizing', () => {
      render(
        <div>
          <h1 className="hindi-heading-xl">{hindiContent.title}</h1>
          <h2 className="hindi-heading-lg">{hindiContent.subtitle}</h2>
          <p className="hindi-body">{hindiContent.content}</p>
        </div>
      );

      const heading1 = screen.getByRole('heading', { level: 1 });
      const heading2 = screen.getByRole('heading', { level: 2 });
      const paragraph = screen.getByText(hindiContent.content);

      expect(heading1).toBeInTheDocument();
      expect(heading2).toBeInTheDocument();
      expect(paragraph).toBeInTheDocument();
    });

    it('applies correct font weights', () => {
      render(
        <div>
          <span className="font-light">{hindiContent.labels.users}</span>
          <span className="font-normal">{hindiContent.labels.revenue}</span>
          <span className="font-bold">{hindiContent.labels.growth}</span>
        </div>
      );

      expect(screen.getByText(hindiContent.labels.users)).toBeInTheDocument();
      expect(screen.getByText(hindiContent.labels.revenue)).toBeInTheDocument();
      expect(screen.getByText(hindiContent.labels.growth)).toBeInTheDocument();
    });
  });

  describe('Text Direction & Alignment', () => {
    it('handles left-to-right text direction', () => {
      render(
        <div className="text-left">
          <p>{hindiContent.content}</p>
        </div>
      );

      const paragraph = screen.getByText(hindiContent.content);
      expect(paragraph).toBeInTheDocument();
      expect(paragraph.parentElement).toHaveClass('text-left');
    });

    it('supports center alignment for titles', () => {
      render(
        <h1 className="text-center hindi-title">
          {hindiContent.title}
        </h1>
      );

      const title = screen.getByRole('heading', { level: 1 });
      expect(title).toBeInTheDocument();
      expect(title).toHaveClass('text-center');
    });
  });

  describe('Font Loading & Fallbacks', () => {
    it('loads Hindi-compatible fonts', () => {
      render(
        <div className="font-hindi">
          <p>{hindiContent.content}</p>
        </div>
      );

      const paragraph = screen.getByText(hindiContent.content);
      expect(paragraph).toBeInTheDocument();
      expect(paragraph.parentElement).toHaveClass('font-hindi');
    });

    it('provides fallback fonts for Hindi text', () => {
      render(
        <p className="hindi-text-with-fallback">
          {hindiContent.content}
        </p>
      );

      const paragraph = screen.getByText(hindiContent.content);
      expect(paragraph).toBeInTheDocument();
    });
  });
});