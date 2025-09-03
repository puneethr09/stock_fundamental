import json
from src.research_guidance_system import ResearchGuidanceSystem


def test_generate_assignment_from_gap():
    rg = ResearchGuidanceSystem()
    gaps = [{"category": "MOAT_ANALYSIS", "company": "TCS", "severity": "high"}]
    assignment = rg.generate_personalized_research_assignment(gaps, learning_stage=2)
    assert assignment["company"] == "TCS"
    assert "instructions" in assignment
    assert isinstance(assignment["instructions"], list)


def test_assignment_evaluation():
    rg = ResearchGuidanceSystem()
    gaps = [{"category": "GENERAL", "company": "ABC", "severity": "low"}]
    assignment = rg.generate_personalized_research_assignment(gaps, learning_stage=1)
    aid = assignment["assignment_id"]
    # submission missing required fields
    result = rg.evaluate_research_submission(aid, {"summary": "", "evidence": ""})
    assert result["score"] == 0
    # submission with required fields
    result2 = rg.evaluate_research_submission(aid, {"summary": "x", "evidence": "y"})
    assert result2["score"] == 100


def test_persistence_save_and_completion(tmp_path, monkeypatch):
    # redirect DB path to tmp for test isolation
    import src.persistence as persistence

    orig_db = persistence.DB_PATH
    persistence.DB_PATH = tmp_path / "research.db"
    try:
        rg = ResearchGuidanceSystem()
        gaps = [{"category": "GENERAL", "company": "XYZ", "severity": "low"}]
        assignment = rg.generate_personalized_research_assignment(
            gaps, learning_stage=1
        )
        aid = assignment["assignment_id"]
        # simulate completion
        rg.track_research_progress(
            "user-test", aid, {"summary": "ok", "evidence": "ok"}
        )
        rows = persistence.get_completions_for_user("user-test")
        assert len(rows) == 1
        assert rows[0]["assignment_id"] == aid
    finally:
        persistence.DB_PATH = orig_db
