"""Tests for the content generator module."""
import unittest
from unittest.mock import patch, MagicMock

from src.content_generator import ContentGenerator

class TestContentGenerator(unittest.TestCase):
    """Test cases for ContentGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.content_generator = ContentGenerator()

    def test_format_tweet_length(self):
        """Test that tweets are properly formatted to correct length."""
        long_content = "x" * 300
        formatted = self.content_generator._format_tweet(long_content)
        self.assertLessEqual(len(formatted), 280)
        self.assertTrue(formatted.endswith("..."))

    def test_is_content_appropriate(self):
        """Test content appropriateness checking."""
        inappropriate_contents = [
            "I'm sorry, I cannot help with that",
            "As an AI language model, I think",
            "I apologize, but I don't have access"
        ]
        
        appropriate_content = (
            "Here's a great Python tip: Use list comprehensions "
            "for cleaner and more efficient code. Example: "
            "squares = [x*x for x in range(10)]"
        )
        
        for content in inappropriate_contents:
            self.assertFalse(
                self.content_generator.is_content_appropriate(content),
                f"Failed for: {content}"
            )
            
        self.assertTrue(
            self.content_generator.is_content_appropriate(appropriate_content)
        )

    def test_extract_tweet_content(self):
        """Test extraction of tweet content from generated text."""
        prompt = "Generate a tweet about Python:"
        generated = prompt + ' "Python f-strings are awesome! Use them for cleaner string formatting."'
        
        expected = "Python f-strings are awesome! Use them for cleaner string formatting."
        result = self.content_generator._extract_tweet_content(generated, prompt)
        
        self.assertEqual(result, expected)

    @patch('transformers.AutoModelForCausalLM.from_pretrained')
    @patch('transformers.AutoTokenizer.from_pretrained')
    def test_generate_tweet(self, mock_tokenizer, mock_model):
        """Test tweet generation with mocked HuggingFace components."""
        # Mock the tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer_instance.pad_token_id = 0
        mock_tokenizer_instance.eos_token_id = 2
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        
        # Mock generate method
        mock_model_instance.generate.return_value = [[1, 2, 3, 4]]
        
        # Mock decode method
        mock_tokenizer_instance.decode.return_value = (
            "Generate a tweet about Python programming: "
            "Use Python's context managers with 'with' statements "
            "for better resource handling and cleaner code."
        )
        
        # Create generator with mocked components
        generator = ContentGenerator()
        
        # Generate tweet
        tweet = generator.generate_tweet("Python programming")
        
        # Verify the result
        self.assertIsInstance(tweet, str)
        self.assertLessEqual(len(tweet), 280)
        
if __name__ == '__main__':
    unittest.main()