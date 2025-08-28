<!-- Powered by BMAD™ Core -->

# Story: Educational Gap-Filling Service

## Status

Draft

## Story

**As a** platform user encountering data limitations during analysis,
**I want** guided research assignments and learning prompts when data is missing,
**so that** I can learn to research missing information independently and turn limitations into learning opportunities.

## Acceptance Criteria

1. System detects when analysis has low confidence due to missing data
2. System generates step-by-step research guides for identified data gaps
3. System provides research questions and recommended sources for manual investigation
4. User can track completion of research assignments and learning progress
5. Existing Five Rules analysis functionality continues to work unchanged
6. New gap identification follows existing analysis confidence pattern
7. Integration with analysis results display maintains current behavior
8. Gap identification logic is covered by unit and integration tests
9. Research guides are contextually relevant to Indian stock market
10. No regression in existing analysis functionality verified

## Tasks / Subtasks

- [ ] Implement EducationalGapFillingService class with gap identification (AC: 1, 2)
  - [ ] Create gap detection logic analyzing ratios_df for None/NaN values
  - [ ] Implement research guide generation based on gap categories
  - [ ] Add step-by-step research assignment creation with Indian market context
  - [ ] Create gap severity scoring system (critical/moderate/minor)
- [ ] Create contextual research guides for Indian stock market (AC: 3, 9)
  - [ ] Economic moats research templates with NSE/BSE company examples
  - [ ] Management quality assessment guides using annual reports
  - [ ] Industry analysis guides with sector-specific Indian sources
  - [ ] Competitive landscape research using publicly available data
  - [ ] Source verification system for Indian regulatory compliance
- [ ] Integrate with existing Five Rules analysis system (AC: 5, 6, 7)
  - [ ] Extend `analyze_ratios()` function in `src/basic_analysis.py`
  - [ ] Add gap-filling section to `templates/results.html` after warnings
  - [ ] Create new Flask route handler for research progress tracking
  - [ ] Maintain existing analysis confidence patterns and warning system
- [ ] Implement progress tracking and comprehensive testing (AC: 4, 8, 10)
  - [ ] Session-based research assignment completion tracking
  - [ ] Unit tests for EducationalGapFillingService gap detection
  - [ ] Integration tests with existing Five Rules analysis workflow
  - [ ] Performance testing to verify < 50ms processing overhead
  - [ ] Regression testing for existing analysis functionality
  - [ ] Test research guide quality with real Indian stock examples

## Dev Notes

### Architecture Context

This story implements the Educational Gap-Filling Approach from the Financial Education Mastery Framework. The system converts data limitations into learning opportunities by detecting low-confidence analysis areas and providing structured research guidance.

**Gap Detection Triggers:**

- Missing financial ratios (when yfinance data is incomplete)
- Low data availability periods (< 3 years of historical data)
- Industry-specific metrics unavailable
- Management/governance information gaps
- Competitive landscape data limitations

**Research Guide Categories:**

- **Economic Moats Research**: Step-by-step competitive analysis guides
- **Management Assessment**: Governance and leadership evaluation frameworks
- **Industry Analysis**: Sector-specific research methodologies
- **Financial Deep-Dive**: Manual calculation guides when automated data fails

### Existing System Integration

**Integration Points:**

- **Analysis Flow**: Extend `analyze_ratios()` in `src/basic_analysis.py` with gap detection
- **Results Display**: Add gap-filling section to `templates/results.html` after warning section
- **Flask Routes**: Extend `/analyze` route in `app.py` to include gap analysis
- **Session Management**: Use existing Flask session to track research progress

**Data Flow Integration:**

```
Five Rules Analysis → Gap Detection → Research Guide Generation → Display Integration
```

### Technical Implementation Details

**Core Implementation:**

- **File**: `src/gap_filling_service.py`
- **Class**: `EducationalGapFillingService`
- **Integration**: Called from `analyze_ratios()` function

**Key Methods:**

```python
def detect_analysis_gaps(ratios_df, warnings, company_name)
def generate_research_guides(identified_gaps, ticker)
def get_indian_market_sources(research_category)
def track_research_progress(session, assignments)
```

**Gap Detection Logic:**

- Check for None/NaN values in critical ratios
- Identify historical data availability gaps
- Detect industry-specific missing metrics
- Flag low confidence warnings as research opportunities

**Indian Market Specific Sources:**

- BSE/NSE annual reports and investor presentations
- Economic Times, Business Standard archives
- Company regulatory filings (BSE/NSE websites)
- Industry reports from CII, FICCI, ASSOCHAM

### Key Constraints

- Research guides must be actionable with free/public sources only
- Gap identification must not slow down analysis (< 50ms overhead)
- Research assignments must be contextual to Indian regulatory environment
- Progress tracking must work without user registration (session-based)
- All sources must be publicly accessible and current

### Testing

#### Testing Standards

- **Test Location**: `tests/test_gap_filling_service.py`
- **Framework**: pytest (following existing test patterns in `tests/test_basic_analysis.py`)
- **Coverage Target**: Minimum 80% for new gap-filling functionality
- **Mock Data**: Use test datasets with intentional gaps to verify detection logic
- **Indian Market Testing**: Validate research guides with real NSE/BSE examples

#### Specific Testing Requirements

**Unit Testing:**

- Gap detection logic with various ratios_df scenarios (missing data, NaN values)
- Research guide generation for different gap categories
- Indian market source validation and accessibility verification
- Session-based progress tracking functionality
- Gap severity scoring system accuracy

**Integration Testing:**

- Seamless integration with existing `analyze_ratios()` workflow
- Template rendering with gap-filling section in `results.html`
- Flask route integration for research progress endpoints
- Community insights interaction (when both features active)

**Performance Testing:**

- Gap detection processing time < 50ms overhead
- Research guide generation performance with large datasets
- Memory usage impact on existing analysis workflow

**Quality Assurance:**

- Research guide accuracy with real Indian stock examples (TCS, Reliance, HDFC)
- Source accessibility verification for all recommended Indian resources
- Progress tracking reliability across user sessions

**Regression Testing:**

- Existing Five Rules analysis functionality unchanged
- Warning system behavior maintained
- Results template display integrity verified

## Change Log

| Date       | Version | Description                                         | Author     |
| ---------- | ------- | --------------------------------------------------- | ---------- |
| 2025-08-28 | 1.0     | Initial story creation and BMAD template conversion | Sarah (PO) |

## Dev Agent Record

_This section will be populated by the development agent during implementation_

## QA Results

_This section will be populated by the QA agent after implementation review_
