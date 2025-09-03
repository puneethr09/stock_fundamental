import unittest
import json
import time
from app import app, research_system
from src.persistence import (
    get_badges_for_user,
    get_notifications_for_user,
    get_completions_for_user,
)


class TestE2EResearchFlow(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.user_id = "e2e_user_1"

    def test_assignment_create_and_complete_and_check_badges(self):
        # Generate assignment directly
        assignment = research_system.generate_personalized_research_assignment(
            user_gaps=[
                {"category": "GENERAL", "company": "TESTCO", "severity": "high"}
            ],
            learning_stage=2,
        )
        aid = assignment["assignment_id"]

        # Submit completion payload
        payload = {
            "user_id": self.user_id,
            "completion": {
                "summary": "Short summary",
                "evidence": ["http://example.com"],
                "duration": 30,
            },
        }

        resp = self.app.post(f"/research-assignment/{aid}/complete", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("evaluation", data)

        # Check completions persisted
        comps = get_completions_for_user(self.user_id)
        self.assertTrue(any(c["assignment_id"] == aid for c in comps))

        # Check badges and notifications (may be empty but endpoints should respond)
        badges = get_badges_for_user(self.user_id)
        notes = get_notifications_for_user(self.user_id)
        self.assertIsInstance(badges, list)
        self.assertIsInstance(notes, list)


if __name__ == "__main__":
    unittest.main()
