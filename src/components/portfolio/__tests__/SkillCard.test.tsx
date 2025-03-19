import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SkillCard } from '../SkillCard';
import type { Skill } from '../../../types';

// Mock Lucide React icons
jest.mock('lucide-react', () => ({
  Star: () => <span data-testid="star-icon">★</span>,
  Shield: () => <span data-testid="shield-icon">🛡</span>,
  Award: () => <span data-testid="award-icon">🏆</span>,
}));

describe('SkillCard', () => {
  const mockSkill: Skill = {
    name: 'React',
    level: 'advanced',
    endorsements: 42,
    verified: true
  };

  const mockOnEndorse = jest.fn();
  const mockOnViewDetails = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders skill card with all required props', () => {
    render(<SkillCard skill={mockSkill} />);
    
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Advanced')).toBeInTheDocument();
    expect(screen.getByText('42 endorsements')).toBeInTheDocument();
    expect(screen.getByTestId('shield-icon')).toBeInTheDocument();
  });

  it('handles endorsement click', () => {
    render(<SkillCard skill={mockSkill} onEndorse={mockOnEndorse} />);
    
    fireEvent.click(screen.getByText('Endorse'));
    expect(mockOnEndorse).toHaveBeenCalledWith('React');
  });

  it('handles view details click', () => {
    render(<SkillCard skill={mockSkill} onViewDetails={mockOnViewDetails} />);
    
    fireEvent.click(screen.getByText('View Details'));
    expect(mockOnViewDetails).toHaveBeenCalledWith('React');
  });

  it('applies correct color class based on skill level', () => {
    const levels: Array<Skill['level']> = ['beginner', 'intermediate', 'advanced', 'expert'];
    const colorClasses = {
      beginner: 'bg-green-100 text-green-800',
      intermediate: 'bg-yellow-100 text-yellow-800',
      advanced: 'bg-orange-100 text-orange-800',
      expert: 'bg-red-100 text-red-800'
    };

    levels.forEach(level => {
      const { container } = render(
        <SkillCard skill={{ ...mockSkill, level }} />
      );
      
      const levelBadge = container.querySelector(`.${colorClasses[level].split(' ')[0]}`);
      expect(levelBadge).toBeInTheDocument();
    });
  });

  it('does not show verified shield when skill is not verified', () => {
    render(<SkillCard skill={{ ...mockSkill, verified: false }} />);
    expect(screen.queryByTestId('shield-icon')).not.toBeInTheDocument();
  });

  // PropTypes validation tests
  describe('PropTypes validation', () => {
    const consoleError = console.error;
    beforeEach(() => {
      console.error = jest.fn();
    });
    
    afterEach(() => {
      console.error = consoleError;
    });

    it('throws error when skill prop is missing', () => {
      // @ts-ignore - Testing PropTypes
      expect(() => render(<SkillCard />)).toThrow();
      expect(console.error).toHaveBeenCalled();
    });

    it('throws error when skill level is invalid', () => {
      const invalidSkill = {
        ...mockSkill,
        // @ts-ignore - Testing invalid level
        level: 'master'
      };
      
      render(<SkillCard skill={invalidSkill} />);
      expect(console.error).toHaveBeenCalled();
    });

    it('throws error when endorsements is not a number', () => {
      const invalidSkill = {
        ...mockSkill,
        // @ts-ignore - Testing invalid endorsements
        endorsements: '42'
      };
      
      render(<SkillCard skill={invalidSkill} />);
      expect(console.error).toHaveBeenCalled();
    });
  });

  // Edge cases
  it('handles zero endorsements correctly', () => {
    render(<SkillCard skill={{ ...mockSkill, endorsements: 0 }} />);
    expect(screen.getByText('0 endorsements')).toBeInTheDocument();
  });

  it('handles long skill names', () => {
    const longSkillName = 'Extremely Long Skill Name That Should Still Render Properly';
    render(<SkillCard skill={{ ...mockSkill, name: longSkillName }} />);
    expect(screen.getByText(longSkillName)).toBeInTheDocument();
  });
});