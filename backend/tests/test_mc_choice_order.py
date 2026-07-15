"""Tests for MC choice shuffle and position-balance gate."""

import unittest

from question_tools.mc_choices import (
    assert_mc_position_balanced,
    correct_position_counts,
    shuffle_mc_choices,
)


class McChoiceOrderTests(unittest.TestCase):
    def test_shuffle_preserves_correct_mapping(self):
        choices = [
            {"text": "right", "is_correct": True},
            {"text": "w1", "is_correct": False},
            {"text": "w2", "is_correct": False},
            {"text": "w3", "is_correct": False},
        ]
        out = shuffle_mc_choices(choices, rng=__import__("random").Random(0))
        self.assertEqual(len(out), 4)
        self.assertEqual(sum(1 for c in out if c["is_correct"]), 1)
        correct = next(c for c in out if c["is_correct"])
        self.assertEqual(correct["text"], "right")
        self.assertEqual({c["text"] for c in out}, {"right", "w1", "w2", "w3"})

    def test_assert_rejects_biased_bank(self):
        bank = []
        for i in range(40):
            bank.append(
                {
                    "question_type": "Multiple Choice",
                    "choices": [
                        {"text": f"a{i}", "is_correct": True},
                        {"text": f"b{i}", "is_correct": False},
                        {"text": f"c{i}", "is_correct": False},
                        {"text": f"d{i}", "is_correct": False},
                    ],
                }
            )
        with self.assertRaises(ValueError):
            assert_mc_position_balanced(bank, label="biased")

    def test_assert_accepts_balanced_bank(self):
        bank = []
        for i in range(40):
            choices = [
                {"text": f"a{i}", "is_correct": False},
                {"text": f"b{i}", "is_correct": False},
                {"text": f"c{i}", "is_correct": False},
                {"text": f"d{i}", "is_correct": False},
            ]
            choices[i % 4]["is_correct"] = True
            bank.append({"question_type": "Multiple Choice", "choices": choices})
        counts = assert_mc_position_balanced(bank)
        self.assertEqual(correct_position_counts(bank), counts)
        for letter in ("A", "B", "C", "D"):
            self.assertEqual(counts[letter], 10)


if __name__ == "__main__":
    unittest.main()
