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
  - [ ] Implement 4-stage learning progression assessment algorithm with behavioral scoring
  - [ ] Add stage categorization based on tooltip usage, analysis completion, prediction accuracy
  - [ ] Create stage transition logic with progress thresholds
- [ ] Integrate behavioral data collection with existing analysis workflow (AC: 1, 5, 6)
  - [ ] Extend existing Flask session in `app.py` to track educational interactions
  - [ ] Add lightweight behavioral tracking to `analyze_ratios()` function calls
  - [ ] Hook into existing results template to capture tooltip and warning interactions
  - [ ] Ensure tracking follows existing Flask session patterns without breaking functionality
- [ ] Create stage-appropriate content delivery system (AC: 3, 4)
  - [ ] Implement adaptive content difficulty based on assessed learning stage
  - [ ] Add learning stage progress indicators to `templates/results.html`
  - [ ] Create stage-specific educational content variations
  - [ ] Integrate with existing educational tooltip and gap-filling systems
- [ ] Implement comprehensive testing coverage (AC: 8, 10)
  - [ ] Create unit tests for EducationalMasteryFramework stage assessment algorithms
  - [ ] Add integration tests for behavioral tracking with Flask session workflow
  - [ ] Test stage transition logic and content adaptation accuracy
  - [ ] Verify no regression in existing analysis functionality with comprehensive test suite
- [ ] Ensure privacy and performance requirements (AC: 9)
  - [ ] Implement anonymous behavioral analytics using browser localStorage + Flask session
  - [ ] Create privacy-first data collection (no personal identifiers stored)
  - [ ] Verify performance impact < 50ms additional processing per analysis
  - [ ] Add data retention policies for behavioral analytics (7-day rolling window)

## Dev Notes

### Architecture Context

This story implements the foundation for the Financial Education Mastery Framework from the brownfield architecture. The system establishes a 4-stage learning progression that adapts content and interface based on user behavioral analytics.

**Learning Stage Definitions:**

**Stage 1 - Guided Discovery** (2-4 weeks):

- Heavy tooltip usage, needs explanations for basic ratios
- High warning attention, clicks on info buttons frequently
- Completes basic analysis but doesn't explore research guides
- **UI Adaptations**: More tooltips, simplified language, basic educational content

**Stage 2 - Assisted Analysis** (4-8 weeks):

- Moderate tooltip usage, starts recognizing patterns
- Engages with research guides from gap-filling system
- Begins making connections between different ratios
- **UI Adaptations**: Intermediate explanations, pattern highlighting, guided research

**Stage 3 - Independent Thinking** (8-16 weeks):

- Low tooltip usage, confident with basic ratios
- Actively uses research guides and community insights
- Makes analysis predictions and comparisons across stocks
- **UI Adaptations**: Advanced content, confidence building exercises, peer insights

**Stage 4 - Analytical Mastery** (Ongoing):

- Minimal tooltip usage, teaches others via community contributions
- Creates high-quality community insights and research findings
- Handles complex analysis scenarios independently
- **UI Adaptations**: Expert mode, teaching tools, advanced pattern recognition

**Behavioral Analytics Tracking:**

- Tooltip interaction frequency and duration
- Warning section engagement (info button clicks)
- Research guide completion rates
- Community insight contribution quality
- Analysis session duration and depth
- Cross-stock comparison behavior

### Existing System Integration

**Integration Points:**

- **Flask Session**: Extend existing session management in `app.py` routes
- **Analysis Results**: Hook into `analyze_ratios()` output processing in `src/basic_analysis.py`
- **UI Templates**: Enhance `templates/results.html` with stage-appropriate content
- **Gap-Filling System**: Connect with existing educational gap detection
- **Community System**: Integrate with existing community insight quality tracking

**Data Flow Integration:**

```
User Analysis → Behavioral Tracking → Stage Assessment → Adaptive Content → Learning Progress
```

**Storage Architecture:**

- **Browser localStorage**: Persistent behavioral data (7-day rolling window)
- **Flask Session**: Current session behavioral tracking
- **No Database**: Maintains existing architecture, no user accounts required

### Technical Implementation Details

**Core Implementation:**

- **File**: `src/educational_framework.py`
- **Class**: `EducationalMasteryFramework`
- **Integration**: Called from Flask routes and analysis processing

**Key Methods:**

```python
def track_user_behavior(session_data, interaction_type, interaction_data)
def assess_learning_stage(behavioral_history)
def get_stage_appropriate_content(current_stage, analysis_context)
def update_stage_progress(user_actions, current_stage)
```

**Behavioral Scoring Algorithm:**

- **Tooltip Dependency Score**: Frequency and duration of tooltip usage
- **Analysis Depth Score**: Engagement with warnings, research guides, community insights
- **Pattern Recognition Score**: Cross-stock analysis patterns, prediction accuracy
- **Teaching Contribution Score**: Community insight quality and helpfulness

**Stage-Adaptive Content System:**

- **Tooltip Complexity**: Adjusts explanation depth based on stage
- **Educational Content**: Filters gap-filling research guides by difficulty
- **UI Elements**: Shows/hides advanced features based on readiness
- **Progress Indicators**: Visual feedback on learning progression

### Key Constraints

**Privacy-First Design:**

- No personal identifiers stored (anonymous behavioral tracking only)
- All data stored in browser localStorage + Flask session (no server-side user data)
- 7-day rolling window data retention policy
- GDPR-compliant anonymous analytics

**Performance Requirements:**

- Stage assessment processing < 50ms per analysis request
- Behavioral tracking adds < 25ms to existing analysis workflow
- localStorage operations must be non-blocking
- Adaptive content delivery < 20ms additional template rendering

**Integration Constraints:**

- Must work seamlessly with existing Community Knowledge Base system
- Must enhance (not replace) existing Educational Gap-Filling research guides
- Stage progression must feel natural and non-intrusive
- All existing tooltip and warning functionality preserved

**Technical Constraints:**

- Works offline with cached behavioral data
- Cross-browser localStorage compatibility required
- Mobile-responsive stage indicators and adaptive content
- Graceful degradation when localStorage unavailable

### Testing

#### Testing Standards

- **Test Location**: `tests/test_educational_framework.py`
- **Framework**: pytest (following existing patterns in `tests/test_gap_filling_service.py`)
- **Coverage Target**: Minimum 80% for new educational framework functionality
- **Mock Data**: Simulate behavioral interactions and stage progression scenarios
- **Privacy Testing**: Verify no personal data leakage in behavioral tracking

#### Specific Testing Requirements

**Unit Testing:**

- EducationalMasteryFramework stage assessment algorithms with various behavioral patterns
- Behavioral scoring logic for tooltip usage, analysis depth, pattern recognition
- Stage transition thresholds and progression accuracy
- Stage-appropriate content filtering and delivery logic
- Privacy compliance verification (no personal identifiers in stored data)

**Integration Testing:**

- Seamless integration with existing Flask session management
- Behavioral tracking integration with `analyze_ratios()` workflow
- Template rendering with stage-appropriate content adaptation
- Cross-system integration with Community Knowledge Base and Gap-Filling systems
- localStorage and Flask session data synchronization

**Performance Testing:**

- Stage assessment processing time < 50ms per analysis request
- Behavioral tracking overhead < 25ms per user interaction
- Adaptive content delivery performance < 20ms template rendering
- localStorage operation efficiency and non-blocking behavior

**Privacy and Compliance Testing:**

- Anonymous behavioral data collection verification
- GDPR compliance for data retention and user control
- 7-day rolling window data retention policy enforcement
- Cross-browser localStorage privacy and security

**User Experience Testing:**

- Stage progression feels natural and helpful (not intrusive)
- Adaptive content appropriately matches user skill level
- Learning progress indicators provide meaningful feedback
- Mobile responsiveness of stage indicators and adaptive content

**Regression Testing:**

- Existing analysis functionality unchanged and enhanced
- Community Knowledge Base system integration maintained
- Educational Gap-Filling system compatibility preserved
- All existing tooltips and warning system behavior maintained

## Change Log

| Date       | Version | Description                                         | Author     |
| ---------- | ------- | --------------------------------------------------- | ---------- |
| 2025-08-28 | 1.0     | Initial story creation and BMAD template conversion | Sarah (PO) |

## Dev Agent Record

_This section will be populated by the development agent during implementation_

## QA Results

_This section will be populated by the QA agent after implementation review_
