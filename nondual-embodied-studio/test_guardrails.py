import json
import unittest
from pathlib import Path

from anti_sycophancy_linter import lint_dialogue_script
from phonetic_guard import normalize_for_speech
from render_embodied_essay import synthesize_stillness_bed

BASE = Path(__file__).resolve().parent

class TestEmbodiedGuardrails(unittest.TestCase):
    def test_unicode_phonetics(self):
        spoken = normalize_for_speech("Flyxion explored rasa-darśan, Tōrō lanterns, and Bonshō bells.")
        self.assertIn("FLIK-shun", spoken)
        self.assertIn("RAH-sah DAR-shahn", spoken)
        self.assertIn("TOH-roh", spoken)
        self.assertIn("BON-shoh", spoken)

    def test_rejects_flattery_and_missing_limits(self):
        res = lint_dialogue_script({
            "limitations": ["Only one limit."],
            "turns": [{"speaker": "A", "text": "This groundbreaking masterpiece is genius!"}],
        })
        self.assertFalse(res["valid"])
        self.assertGreaterEqual(len(res["errors"]), 3)

    def test_zenodo_dialogue_passes(self):
        doc = json.loads((BASE / "scripts" / "zenodo-24393275-dialogue.json").read_text(encoding="utf-8"))
        res = lint_dialogue_script(doc)
        self.assertTrue(res["valid"], msg=str(res["errors"]))

    def test_stillness_bed_generation(self):
        bed = synthesize_stillness_bed(2205)
        self.assertEqual(len(bed), 2205)
        self.assertTrue(all(-32767 <= s <= 32767 for s in bed))

if __name__ == "__main__":
    unittest.main()
