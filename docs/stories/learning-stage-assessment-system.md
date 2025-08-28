<!-- Powered by BMAD™ Core -->

# Story: Learning Stage Assessment System

## Status

Draft

## Story

**As a** platform user learning stock analysis,
**I want** the system to automatically assess my current learning stage and provide appropriate content difficulty,
**so that** I receive personalized educational content that matches my skill level and progresses me toward independent analysis.

## Acceptance Criteria

1. System tracks user behavior patterns (analysis completion, tooltip usage, prediction accuracy)
2. System automatically categorizes users into one of 4 learning stages based on behavioral analytics
3. System provides stage-appropriate educational content and interface elements
4. User can view their current learning stage and progress indicators
5. Existing stock analysis functionality continues to work unchanged
6. New learning assessment follows existing user session management pattern
7. Integration with current analysis workflow maintains current behavior
8. Learning stage assessment is covered by unit and integration tests
9. User behavioral tracking respects privacy (no personal data stored)
10. No regression in existing analysis functionality verified

## Tasks / Subtasks

- [ ] Implement EducationalMasteryFramework class with stage assessment logic (AC: 1, 2)
  - [ ] Create behavioral analytics tracking system for user interactions
  - [ ] Implement 4-stage learning progression assessment algorithm
  - [ ] Add stage categorization based on behavior patterns
- [ ] Integrate behavioral data collection with existing analysis workflow (AC: 1, 5, 6)
  - [ ] Extend existing session management to track educational interactions
  - [ ] Add lightweight behavioral tracking to analysis result processing
  - [ ] Ensure tracking follows existing Flask session patterns
- [ ] Create stage-appropriate content delivery system (AC: 3, 4)
  - [ ] Implement content difficulty adjustment based on assessed stage
  - [ ] Add learning stage progress indicators to UI
  - [ ] Integrate with existing educational tooltip system
- [ ] Implement comprehensive testing coverage (AC: 8, 10)
  - [ ] Create unit tests for EducationalMasteryFramework class
  - [ ] Add integration tests for behavioral tracking workflow
  - [ ] Verify no regression in existing analysis functionality
- [ ] Ensure privacy and performance requirements (AC: 9)
  - [ ] Implement anonymous behavioral analytics using localStorage
  - [ ] Verify performance impact is minimal (< 50ms additional processing)
  - [ ] Add privacy-focused data handling verification

## Dev Notes

### Architecture Context

This story implements the foundation for the Financial Education Mastery Framework from the brownfield architecture. The system establishes 4-stage learning progression:

1. **Stage 1 - Guided Discovery** (2-4 weeks): Pattern recognition with heavy guidance
2. **Stage 2 - Assisted Analysis** (4-8 weeks): Connecting patterns across stocks
3. **Stage 3 - Independent Thinking** (8-16 weeks): Tool-light analysis with confidence building
4. **Stage 4 - Analytical Mastery** (Ongoing): Teaching others and advanced pattern recognition

### Existing System Integration

- **Current Flask Structure**: Extend existing session management in `src/utils.py`
- **Analysis Integration**: Hook into existing analysis result processing in `src/basic_analysis.py`
- **UI Integration**: Enhance current educational tooltips system in `templates/`
- **Storage Pattern**: Follow existing browser localStorage usage for user preferences

### Technical Implementation Details

- **EducationalMasteryFramework Class**: Implement in new `src/educational_framework.py`
- **Behavioral Tracking**: Lightweight analytics using existing Flask session patterns
- **Stage Assessment Logic**: Algorithm based on tooltip usage, prediction accuracy, analysis completion rates
- **Content Delivery**: Stage-appropriate educational content integrated with existing template system

### Key Constraints

- Must work with browser localStorage (no user accounts required)
- Behavioral tracking must be privacy-focused and anonymous
- Learning assessment must work offline with cached data
- Performance impact < 50ms additional processing time

### Testing

#### Testing Standards

- **Test Location**: `tests/test_educational_framework.py`
- **Framework**: pytest (following existing test patterns in `tests/`)
- **Coverage Target**: Minimum 80% for new educational functionality
- **Integration Testing**: Verify no regression in existing analysis workflow

#### Specific Testing Requirements

- Unit tests for EducationalMasteryFramework stage assessment logic
- Integration tests for behavioral tracking with existing Flask sessions
- Privacy testing to ensure no personal data storage
- Performance testing to verify < 50ms impact
- Regression testing for existing analysis functionality

## Change Log

| Date       | Version | Description                                         | Author     |
| ---------- | ------- | --------------------------------------------------- | ---------- |
| 2025-08-28 | 1.0     | Initial story creation and BMAD template conversion | Sarah (PO) |

## Dev Agent Record

_This section will be populated by the development agent during implementation_

## QA Results

_This section will be populated by the QA agent after implementation review_
