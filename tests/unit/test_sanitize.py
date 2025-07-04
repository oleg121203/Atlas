import unittest

from core.sanitize import sanitize_input, sanitize_output


class TestSanitize(unittest.TestCase):
    """Tests for the sanitize module."""

    def test_sanitize_input(self):
        assert (
            sanitize_input('<script>alert("xss")</script>')
            == "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
        )

    def test_sanitize_output(self):
        assert (
            sanitize_output('<script>alert("xss")</script>')
            == "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
        )

    def test_sanitize_html(self):
        """Test sanitizing HTML tags."""
        input_text = "<script>alert('XSS');</script>Hello"
        sanitized = sanitize_input(input_text)
        # The script tag should be removed
        self.assertNotIn("<script>", sanitized)
        self.assertNotIn("</script>", sanitized)
        # The text should be preserved
        self.assertIn("Hello", sanitized)

    def test_sanitize_html_attributes(self):
        """Test sanitizing HTML attributes that could contain JavaScript."""
        input_text = "<a href=\"javascript:alert('XSS');\">Click me</a>"
        sanitized = sanitize_input(input_text)
        # The javascript: protocol should be removed or escaped
        self.assertNotIn("javascript:", sanitized.lower())
        # The text should be preserved
        self.assertIn("Click me", sanitized)

    def test_sanitize_sql_injection(self):
        """Test sanitizing SQL injection attempts."""
        input_text = "username' OR '1'='1"
        sanitized = sanitize_input(input_text)
        # Single quotes might be escaped or encoded
        # We're just checking it's different from the original
        self.assertNotEqual(sanitized, input_text)

    def test_sanitize_empty_string(self):
        """Test sanitizing an empty string."""
        self.assertEqual(sanitize_input(""), "")

    def test_sanitize_special_chars(self):
        """Test sanitizing special characters."""
        input_text = "&<>\"'"
        sanitized = sanitize_input(input_text)
        # Special characters should be encoded or escaped
        self.assertNotEqual(sanitized, input_text)
        # Length should be greater than original due to encoding
        self.assertGreaterEqual(len(sanitized), len(input_text))

    def test_sanitize_script_with_entities(self):
        """Test sanitizing scripts with HTML entities."""
        input_text = '<script>alert("XSS")</script>'
        sanitized = sanitize_input(input_text)
        # The script tag should be removed or escaped
        self.assertNotIn("<script>", sanitized.lower())


if __name__ == "__main__":
    unittest.main()
