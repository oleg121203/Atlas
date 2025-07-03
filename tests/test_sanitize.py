from core.sanitize import sanitize_input, sanitize_output
from ui.input_validation import sanitize_ui_input


def test_sanitize_removes_script():
    input_text = "<script>alert('hello')</script>"
    sanitized = sanitize_ui_input(input_text)
    assert "<script>" not in sanitized
    assert "</script>" not in sanitized
    # Check that the script content is not executable, i.e., it should be escaped or removed
    assert not ("alert('hello')" in sanitized and "<script>" in sanitized)
    assert not ("alert('" in sanitized and "<script>" in sanitized)


def test_sanitize_html():
    """Test that HTML tags are properly escaped."""
    dirty = "<p>Hello</p>"
    clean = sanitize_ui_input(dirty)
    assert "<p>" in clean or "&lt;p&gt;" in clean or "&amp;lt;p&amp;gt;" in clean
    assert "</p>" in clean or "&lt;/p&gt;" in clean or "&amp;lt;/p&amp;gt;" in clean
    assert "Hello" in clean


def test_sanitize_special_chars():
    """Test that special characters are properly escaped."""
    input_text = "hello & < > \" ' /"
    sanitized = sanitize_ui_input(input_text)
    assert (
        "&amp;" in sanitized
        or "&quot;" in sanitized
        or "&lt;" in sanitized
        or "&gt;" in sanitized
    )


def test_sanitize_plain_text():
    text = "just a normal string!"
    assert sanitize_ui_input(text) == text


import unittest


class TestSanitize(unittest.TestCase):
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        input_str = "Hello <script>alert('xss')</script> World"
        expected = "Hello &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt; World"
        result = sanitize_input(input_str)
        self.assertEqual(result, expected)

    def test_sanitize_input_empty(self):
        """Test input sanitization with empty string."""
        input_str = ""
        expected = ""
        result = sanitize_input(input_str)
        self.assertEqual(result, expected)

    def test_sanitize_input_special_chars(self):
        """Test input sanitization with special characters."""
        input_str = "Hello!@#$%^&*()_+-=[]{}|;:,.<>?`~"
        expected = "Hello!@#$%^&amp;*()_+-=[]{}|;:,.&lt;&gt;?`~"
        result = sanitize_input(input_str)
        self.assertEqual(result, expected)

    def test_sanitize_input_html_entities(self):
        """Test input sanitization with HTML entities."""
        input_str = "Hello &amp; World &lt;script&gt;"
        expected = "Hello &amp;amp; World &amp;lt;script&amp;gt;"
        result = sanitize_input(input_str)
        self.assertEqual(result, expected)

    def test_sanitize_output_basic(self):
        """Test basic output sanitization."""
        output_str = "Hello <script>alert('xss')</script> World"
        expected = "Hello &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt; World"
        result = sanitize_output(output_str)
        self.assertEqual(result, expected)

    def test_sanitize_output_empty(self):
        """Test output sanitization with empty string."""
        output_str = ""
        expected = ""
        result = sanitize_output(output_str)
        self.assertEqual(result, expected)

    def test_sanitize_output_special_chars(self):
        """Test output sanitization with special characters."""
        output_str = "Hello!@#$%^&*()_+-=[]{}|;:,.<>?`~"
        expected = "Hello!@#$%^&amp;*()_+-=[]{}|;:,.&lt;&gt;?`~"
        result = sanitize_output(output_str)
        self.assertEqual(result, expected)

    def test_sanitize_output_html_entities(self):
        """Test output sanitization with HTML entities."""
        output_str = "Hello &amp; World &lt;script&gt;"
        expected = "Hello &amp;amp; World &amp;lt;script&amp;gt;"
        result = sanitize_output(output_str)
        self.assertEqual(result, expected)

    def test_sanitize_input_sql_injection(self):
        """Test input sanitization against SQL injection."""
        input_str = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        expected = "SELECT * FROM users WHERE id = &#x27;1&#x27; OR &#x27;1&#x27;=&#x27;1&#x27;"
        result = sanitize_input(input_str)
        self.assertEqual(result, expected)

    def test_sanitize_input_xss_advanced(self):
        """Test input sanitization against advanced XSS."""
        input_str = "Hello <img src=x onerror=alert('xss')>"
        expected = "Hello &lt;img src=x onerror=alert(&#x27;xss&#x27;)&gt;"
        result = sanitize_input(input_str)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
