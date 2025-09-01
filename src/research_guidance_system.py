from typing import List, Dict, Any
from types import SimpleNamespace
import uuid
from src.persistence import save_assignment, get_assignment, save_completion


class ResearchGuidanceSystem:
    """Generate personalized research assignments based on identified gaps

    This is intentionally lightweight and deterministic so unit tests can
    validate behaviour. Integrates with gap identification results supplied
    by the caller (the gap-filling service).
    """

    def __init__(self):
        # Simple in-memory store for created assignments (id -> assignment)
        self._assignments: Dict[str, Dict[str, Any]] = {}

    def generate_personalized_research_assignment(
        self,
        user_gaps: List[Dict[str, Any]],
        learning_stage: int,
        research_history: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create one prioritized research assignment from gaps.

        Input:
          - user_gaps: list of gap dicts with keys: category, company, severity
          - learning_stage: int 1..4 adapting difficulty
        Output: assignment dict with instructions and metadata
        """
        research_history = research_history or []

        # pick highest severity gap
        if not user_gaps:
            gap = {"category": "GENERAL", "company": None, "severity": "low"}
        else:
            gap = sorted(
                user_gaps, key=lambda g: g.get("severity", "low"), reverse=True
            )[0]

        assignment_id = str(uuid.uuid4())
        difficulty = self._map_stage_to_difficulty(learning_stage)

        title = f"Research: {gap.get('category', 'Company Research')}"
        if gap.get("company"):
            title = f"Research: {gap['company']} - {gap.get('category') or 'Analysis'}"

        instructions = self.create_step_by_step_research_instructions(
            gap.get("category", "GENERAL"), gap.get("company"), difficulty
        )

        assignment = {
            "assignment_id": assignment_id,
            "title": title,
            "company": gap.get("company"),
            "category": gap.get("category"),
            "difficulty": difficulty,
            "instructions": instructions,
            "success_criteria": self._default_success_criteria(gap.get("category")),
            "time_estimate_minutes": self._time_estimate_for_difficulty(difficulty),
        }

        # store assignment for tracking
        self._assignments[assignment_id] = assignment
        # persist assignment
        try:
            save_assignment(assignment)
        except Exception:
            # non-fatal in test environment
            pass
        return assignment

    # Backwards-compatible alias
    def create_research_assignment(
        self,
        assignment_type: str,
        user_profile: Dict[str, Any],
        company_context: Dict[str, Any],
    ):
        """Compatibility wrapper for older tests that call create_research_assignment.

        We map their inputs into the generate_personalized_research_assignment signature
        by constructing a minimal gap object derived from company_context.
        """
        gap = {
            "category": assignment_type,
            "company": company_context.get("ticker")
            or company_context.get("company_name"),
            "severity": "medium",
        }

        learning_stage = 2
        if isinstance(user_profile, dict):
            learning_stage = user_profile.get("learning_stage", 2)

        # If learning_stage is enum-like, try to extract numeric value
        if hasattr(learning_stage, "value"):
            try:
                learning_stage = int(learning_stage.value)
            except Exception:
                # fallback to default
                learning_stage = 2

        assignment = self.generate_personalized_research_assignment(
            [gap], learning_stage
        )

        # Wrap into a simple object with attribute access expected by tests
        obj = SimpleNamespace()
        obj.assignment_id = assignment.get("assignment_id")
        obj.title = assignment.get("title")
        obj.company = assignment.get("company")
        obj.instructions = assignment.get("instructions", [])
        # convert minutes to seconds for compatibility
        obj.time_estimate = assignment.get("time_estimate_minutes", 0) * 60
        obj.assignment_type = assignment.get("category") or assignment_type
        obj.difficulty = assignment.get("difficulty")
        return obj

    def create_step_by_step_research_instructions(
        self, assignment_type: str, company: str, difficulty: str
    ) -> List[str]:
        """Return an actionable step-list for the requested assignment type.

        This function focuses on being concise and actionable so it can be
        embedded in the UI and tested deterministically.
        """
        base = []
        if assignment_type in ("MOAT_ANALYSIS", "MOAT"):
            base = [
                "Formulate a clear moat hypothesis (e.g. pricing power, network effects)",
                "Collect primary sources: annual reports, management commentary, segment disclosures",
                "Compare margins and ROCE vs top 3 listed peers for the last 3 years",
                "Document qualitative evidence (customer contracts, patents, switching costs)",
                "Conclude with a 1-paragraph moat strength rating and supporting evidence",
            ]
        elif assignment_type in ("MANAGEMENT_ASSESSMENT", "MANAGEMENT"):
            base = [
                "Review leadership biographies and prior roles from annual reports and company website",
                "Check promoter/insider shareholding trends and related-party transactions",
                "Scan past earnings calls for strategic consistency and capital allocation decisions",
                "Assess governance metrics: board independence, audit observations, restatements",
                "Summarize strengths, concerns and a 1-paragraph recommendation",
            ]
        elif assignment_type in ("COMPETITIVE_ANALYSIS", "COMPETITION"):
            base = [
                "Map the top competitors and their market share using industry reports and filings",
                "Identify key differentiation (cost, distribution, product breadth)",
                "Analyze customer concentration and supplier dependence",
                "Produce a 2-column competitor comparison table and narrative",
            ]
        else:
            base = [
                "Collect company annual report and recent analyst notes (if available)",
                "Summarize business model and revenue drivers in 3 bullet points",
                "Identify 2 key risks and 2 key growth drivers",
                "Write a concise 200-300 word research summary",
            ]

        # adapt instructions by difficulty
        if difficulty == "guided":
            # add checklists and example sources
            base.insert(
                0,
                "Use the provided checklist and example sources: BSE/NSE filings, Economic Times, company website",
            )
        elif difficulty == "mastery":
            base.append(
                "Include primary data tables and full source citations; prepare slide-deck style summary"
            )

        return base

    def evaluate_research_submission(
        self, assignment_id: str, submission: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Lightweight automatic evaluation returning a score and feedback.

        Real production systems would include human review; this is an automated
        first-pass evaluator used by tests and to provide immediate feedback.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment:
            return {"score": 0, "feedback": "Assignment not found"}

        # simple heuristics: presence of required sections
        score = 0
        required = ["summary", "evidence"]
        for r in required:
            if r in submission and submission[r]:
                score += 50

        score = min(100, score)
        feedback = (
            "Good structure"
            if score >= 50
            else "Add a concise summary and evidence from sources"
        )
        return {"score": score, "feedback": feedback}

    def track_research_progress(
        self, user_id: str, assignment_id: str, completion_data: Dict[str, Any]
    ) -> None:
        # persist completion and update in-memory
        self._assignments.get(assignment_id, {}).update(
            {"last_completion": completion_data}
        )
        try:
            save_completion(assignment_id, user_id, completion_data)
        except Exception:
            pass

    def adapt_assignment_difficulty(
        self, performance_history: List[Dict[str, Any]], current_stage: int
    ) -> str:
        # return 'guided' | 'standard' | 'mastery'
        if not performance_history:
            return self._map_stage_to_difficulty(current_stage)
        avg = sum([h.get("score", 50) for h in performance_history]) / len(
            performance_history
        )
        if avg > 80:
            return "mastery"
        if avg < 50:
            return "guided"
        return "standard"

    def _map_stage_to_difficulty(self, stage: int) -> str:
        return {1: "guided", 2: "standard", 3: "standard", 4: "mastery"}.get(
            stage, "standard"
        )

    def _default_success_criteria(self, category: str) -> List[str]:
        return [
            "Clear hypothesis or research question",
            "Use of at least two credible primary/official sources",
            "Evidence-backed conclusion with clear next-steps",
        ]

    def _time_estimate_for_difficulty(self, difficulty: str) -> int:
        return {"guided": 60, "standard": 180, "mastery": 480}.get(difficulty, 120)
