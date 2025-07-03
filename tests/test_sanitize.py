from ui.input_validation import sanitize_ui_input


def test_sanitize_removes_script(self):
    """Test that script tags are properly escaped."""
    input_str = "<script>alert('hello')</script>"
    result = sanitize_ui_input(input_str)
    assert "&amp;lt;script&amp;gt;" in result
    assert "alert('hello')" not in result
    assert "&amp;lt;/script&amp;gt;" in result


def test_sanitize_html():
    dirty = "<p>Hello</p>"
    clean = sanitize_ui_input(dirty)
    assert "&amp;lt;p&amp;gt;Hello&amp;lt;/p&amp;gt;" in clean


def test_sanitize_special_chars(self):
    """Test that special characters are properly escaped."""
    input_str = "hello & < > \" ' /"
    result = sanitize_ui_input(input_str)
    assert "&amp;lt;" in result
    assert "&amp;gt;" in result
    assert "&amp;amp;" in result
    assert "&amp;quot;" in result
    assert "&#x27;" in result
    assert "&#x2F;" in result


def test_sanitize_plain_text():
    text = "just a normal string!"
    assert sanitize_ui_input(text) == text
