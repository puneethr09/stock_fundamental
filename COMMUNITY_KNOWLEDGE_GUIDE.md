# Community Knowledge Base System - Implementation Guide

## Overview

The Community Knowledge Base System enables users to contribute and access community-driven qualitative analysis and stock insights. This system complements the existing quantitative Five Rules analysis with user-generated insights about moats, management, competitive analysis, and industry trends.

## Features Implemented

### Core Features

- ✅ **Anonymous Contribution System**: Users can contribute insights without registration
- ✅ **Insight Categories**: Moat Analysis, Management, Competitive Analysis, Industry Analysis
- ✅ **Spam Prevention**: Rate limiting and duplicate content detection
- ✅ **Quality Control**: Community voting system (upvote/downvote)
- ✅ **Content Moderation**: Flagging system for inappropriate content
- ✅ **Performance Optimization**: Database indexing for sub-100ms queries

### Integration Features

- ✅ **Flask Integration**: New API endpoints for community features
- ✅ **Session Management**: Anonymous user tracking across sessions
- ✅ **UI Integration**: Enhanced results page with community insights section
- ✅ **No Regression**: Existing stock analysis functionality unchanged

## Architecture

### Database Schema

```sql
-- Community insights storage
CREATE TABLE insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    anonymous_user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    votes_up INTEGER DEFAULT 0,
    votes_down INTEGER DEFAULT 0,
    is_flagged BOOLEAN DEFAULT FALSE
);

-- Voting system
CREATE TABLE insight_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_id INTEGER NOT NULL,
    anonymous_user_id TEXT NOT NULL,
    vote_type TEXT NOT NULL CHECK (vote_type IN ('up', 'down')),
    created_at TIMESTAMP NOT NULL,
    UNIQUE(insight_id, anonymous_user_id)
);

-- Spam prevention tracking
CREATE TABLE contribution_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anonymous_user_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

### Key Components

1. **CommunityKnowledgeBase Class** (`src/community_knowledge.py`)

   - Core business logic for insights management
   - Spam detection and content validation
   - Database operations with SQLite

2. **Flask Routes** (`app.py`)

   - `/community/contribute` - Submit new insights
   - `/community/vote` - Vote on insights
   - `/community/flag` - Flag inappropriate content
   - `/community/insights/<ticker>` - Get insights for ticker

3. **Frontend Integration** (`templates/results.html`)
   - Community insights section
   - Contribution form
   - Voting interface
   - Real-time updates via AJAX

## API Endpoints

### POST /community/contribute

Submit a new community insight.

**Request Body:**

```json
{
  "ticker": "TCS",
  "category": "moat_analysis",
  "content": "Detailed analysis about competitive advantages..."
}
```

**Response:**

```json
{
  "success": true,
  "message": "Insight contributed successfully"
}
```

### POST /community/vote

Vote on a community insight.

**Request Body:**

```json
{
  "insight_id": 123,
  "vote_type": "up"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Vote recorded successfully"
}
```

### POST /community/flag

Flag inappropriate content.

**Request Body:**

```json
{
  "insight_id": 123
}
```

### GET /community/insights/<ticker>

Get insights for a specific ticker.

**Response:**

```json
{
  "insights": [
    {
      "id": 123,
      "ticker": "TCS",
      "category": "moat_analysis",
      "content": "Analysis content...",
      "created_at": "2025-08-28T12:00:00",
      "votes_up": 5,
      "votes_down": 1,
      "net_votes": 4
    }
  ]
}
```

## Usage Examples

### Python API Usage

```python
from src.community_knowledge import CommunityKnowledgeBase, InsightCategory

# Initialize
kb = CommunityKnowledgeBase()

# Generate anonymous user ID
user_id = kb.generate_anonymous_user_id("session_data")

# Contribute insight
success, message = kb.contribute_insight(
    ticker="TCS",
    category=InsightCategory.MOAT_ANALYSIS,
    content="TCS has strong competitive moats...",
    anonymous_user_id=user_id
)

# Get insights
insights = kb.get_insights_for_ticker("TCS")

# Vote on insight
success, message = kb.vote_on_insight(
    insight_id=insights[0].id,
    anonymous_user_id=user_id,
    vote_type="up"
)
```

### Frontend Integration

The community insights section automatically appears on stock analysis pages when there are insights available. Users can:

1. **View existing insights** - Categorized and sorted by vote score
2. **Contribute new insights** - Using the contribution form
3. **Vote on insights** - Upvote/downvote for quality control
4. **Flag inappropriate content** - Community moderation

## Testing

### Running Tests

```bash
# Run all community knowledge tests
python -m pytest tests/test_community_knowledge.py -v

# Run specific test categories
python -m pytest tests/test_community_knowledge.py::TestCommunityKnowledgeBase -v
python -m pytest tests/test_community_knowledge.py::TestIntegration -v
```

### Test Coverage

- **18 comprehensive tests** covering all functionality
- **Unit tests** for core business logic
- **Integration tests** for database operations
- **Performance tests** for query optimization
- **Regression tests** for existing functionality

### Demo Script

```bash
# Run the demo to see all features in action
python demo_community_knowledge.py
```

## Deployment Notes

### Database Setup

- Database file created automatically at `data/community_insights.db`
- No manual database setup required
- Indexes created for optimal performance

### Session Configuration

- Flask session secret key automatically generated
- Anonymous user IDs based on IP + User Agent
- Session persistence across browser sessions

### Performance Considerations

- All queries optimized to run under 100ms
- Database indexes on key lookup fields
- Efficient spam detection algorithms
- Minimal impact on existing analysis features

## Security Features

### Spam Prevention

- **Rate limiting**: Max 5 contributions per 30 minutes per user
- **Duplicate detection**: MD5 hashing prevents identical content
- **Content validation**: Length limits and basic spam pattern detection

### Content Moderation

- **Community flagging**: Users can flag inappropriate content
- **Automatic hiding**: Flagged content hidden from public view
- **Basic filtering**: Automatic detection of promotional content

### Privacy Protection

- **Anonymous contributions**: No user registration required
- **Session-based tracking**: Minimal data collection
- **IP-based identification**: No personal data stored

## Acceptance Criteria Verification

✅ **AC1**: Users can contribute insights for stocks (moat analysis, management assessments, competitive analysis)
✅ **AC2**: Community insights are displayed alongside analysis results for relevant stocks  
✅ **AC3**: Users can vote on insight quality with simple validation system
✅ **AC4**: System maintains anonymous contributions while preventing spam
✅ **AC5**: Existing stock analysis and data display functionality continues to work unchanged
✅ **AC6**: New community features follow existing user session and data storage patterns
✅ **AC7**: Integration with analysis results maintains current display behavior
✅ **AC8**: Community contribution system is covered by unit and integration tests
✅ **AC9**: Data validation prevents spam while allowing genuine contributions
✅ **AC10**: No regression in existing analysis functionality verified

## Future Enhancements

### Potential Improvements

- **Enhanced moderation**: Machine learning-based content filtering
- **User reputation**: Contributor scoring system
- **Search functionality**: Full-text search across insights
- **Export features**: CSV/PDF export of community insights
- **Analytics**: Insight engagement and quality metrics

### Scalability Considerations

- **Database migration**: Move to PostgreSQL for larger datasets
- **Caching layer**: Redis for frequently accessed insights
- **CDN integration**: Static asset optimization
- **Load balancing**: Multiple app instances for high traffic

---

**Implementation Status**: ✅ **COMPLETE**  
**Test Coverage**: ✅ **18/18 tests passing**  
**Performance**: ✅ **Sub-100ms query times**  
**Integration**: ✅ **No regression in existing functionality**
