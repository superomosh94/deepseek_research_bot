import unittest
from config import Config
from prompt_engine import PromptEngine

class TestCoreComponents(unittest.TestCase):
    def setUp(self):
        self.engine = PromptEngine()

    def test_config_paths(self):
        """Test if output directory is defined and is a Path object"""
        self.assertTrue(hasattr(Config, 'OUTPUT_DIR'))
        from pathlib import Path
        self.assertIsInstance(Config.OUTPUT_DIR, Path)

    def test_prompt_extraction_marker(self):
        """Test extracting prompt with 'IMPROVED PROMPT:' marker"""
        response = "ANALYSIS: some analysis\n\nIMPROVED PROMPT: Search for quantum bits.\n\nMore text."
        extracted = self.engine.extract_research_prompt(response)
        self.assertEqual(extracted, "Search for quantum bits.")

    def test_prompt_extraction_quotes(self):
        """Test extracting prompt from quotes if no marker is found"""
        response = "I think you should use \"This is a very long prompt that should be caught by the quote matcher because it is over fifty characters long.\""
        extracted = self.engine.extract_research_prompt(response)
        self.assertIn("very long prompt", extracted)

    def test_quality_evaluation_short(self):
        """Test quality evaluation for very short response"""
        score, should_continue, reason = self.engine.evaluate_response_quality("too short", "query")
        self.assertLess(score, 0.5)
        self.assertTrue(should_continue)
        self.assertEqual(reason, "Response too short")

    def test_quality_evaluation_long(self):
        """Test quality evaluation for a more comprehensive response"""
        long_response = "Section 1: Introduction. Quantum computing is fascinating. " \
                        "Example: Shor's algorithm. Significant impacts are expected. " \
                        "In conclusion, it is important. " * 50
        score, should_continue, reason = self.engine.evaluate_response_quality(long_response, "Quantum computing")
        self.assertGreater(score, 0.5)

if __name__ == '__main__':
    unittest.main()
