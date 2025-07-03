from ui.input_validation import sanitize_ui_input


def test_sanitize_removes_script():
    """Test that script tags are properly escaped."""
    input_str = "<script>alert('hello')</script>"
    result = sanitize_ui_input(input_str)
    assert "&lt;script&gt;" in result
    assert "alert('hello')" not in result
    assert "&lt;/script&gt;" in result


def test_sanitize_html():
    """Test that HTML tags are properly escaped."""
    dirty = "<p>Hello</p>"
    clean = sanitize_ui_input(dirty)
    assert "&lt;p&gt;Hello&lt;/p&gt;" in clean


def test_sanitize_special_chars():
    """Test that special characters are properly escaped."""
    input_str = "hello & < > \" ' /"
    result = sanitize_ui_input(input_str)
    assert "&lt;" in result
    assert "&gt;" in result
    assert "&amp;" in result
    assert "&quot;" in result
    assert "'" in result
    assert "/" in result


def test_sanitize_plain_text():
    text = "just a normal string!"
    assert sanitize_ui_input(text) == text
