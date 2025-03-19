# SkillCard Component Documentation

## Overview
The SkillCard component displays a user's skill with its level, endorsements, and verification status.

## Props

### Required Props

#### `skill` (object)
- `name` (string): Name of the skill
- `level` (string): Skill proficiency level ('beginner', 'intermediate', 'advanced', 'expert')
- `endorsements` (number): Number of endorsements received
- `verified` (boolean): Whether the skill is verified

### Optional Props

#### `onEndorse` (function)
- Callback function when endorsing a skill
- Parameters: `skillName` (string)

#### `onViewDetails` (function)
- Callback function when viewing skill details
- Parameters: `skillName` (string)

## Usage Examples

```tsx
// Basic usage
<SkillCard
  skill={{
    name: "React",
    level: "advanced",
    endorsements: 42,
    verified: true
  }}
/>

// With callbacks
<SkillCard
  skill={{
    name: "TypeScript",
    level: "intermediate",
    endorsements: 25,
    verified: false
  }}
  onEndorse={(skillName) => console.log(`Endorsed: ${skillName}`)}
  onViewDetails={(skillName) => console.log(`Viewing details: ${skillName}`)}
/>
```

## Validation Rules

1. Skill object is required and must contain all required fields
2. Level must be one of: 'beginner', 'intermediate', 'advanced', 'expert'
3. Endorsements must be a number
4. Verified must be a boolean
5. Callback functions are optional but must be functions if provided

## Testing

Run tests with:
```bash
npm test
```

Test coverage includes:
- Rendering with required props
- Event handling
- PropTypes validation
- Edge cases
- Color classes for different levels
- Verification badge display