"""Tests for short-answer accepted variants and auto-grading."""

import unittest

from app.services.answer_grading import (
    expects_numeric_response,
    grade_numerical_response,
    short_answers_match,
)
from app.services.short_answers import (
    coalesce_accepted_answers,
    normalize_short_answer,
)


class _Q:
    def __init__(self, answer, accepted=None, qtype="numerical_response"):
        self.answer = answer
        self.accepted_answers = accepted
        self.question_type = qtype


class ShortAnswerTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_short_answer("  Photo Synthesis "), "photo synthesis")
        self.assertEqual(normalize_short_answer("ATP."), "atp")

    def test_coalesce(self):
        vals = coalesce_accepted_answers(
            "photosynthesis",
            '["Photosynthesis", "photo synthesis"]',
        )
        self.assertEqual(vals[0], "photosynthesis")
        # Case variant of canonical is deduped; spaced variant kept.
        self.assertEqual(len(vals), 2)
        self.assertIn("photo synthesis", vals)

    def test_text_grade_variants(self):
        q = _Q("photosynthesis", '["Photosynthesis", "photo synthesis"]')
        self.assertFalse(expects_numeric_response(q))
        r = grade_numerical_response(q, "Photo Synthesis")
        self.assertTrue(r.auto_graded)
        self.assertTrue(r.is_correct)
        r2 = grade_numerical_response(q, "respiration")
        self.assertFalse(r2.is_correct)

    def test_numeric_still_toleranced(self):
        q = _Q("10", '["10.0"]')
        self.assertTrue(expects_numeric_response(q))
        r = grade_numerical_response(q, "10.01")
        self.assertTrue(r.is_correct)

    def test_short_answers_match_numeric_and_text(self):
        self.assertTrue(short_answers_match("4.5", "4.50"))
        self.assertTrue(short_answers_match("ADH", "adh"))


if __name__ == "__main__":
    unittest.main()
