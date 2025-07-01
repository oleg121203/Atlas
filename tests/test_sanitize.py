from ui.input_validation import sanitize_ui_input


def test_sanitize_removes_script():
    dirty = "<script>alert(1)</script>hello"
    clean = sanitize_ui_input(dirty)
    assert "script" not in clean.lower()
    assert "alert" not in clean.lower()
    assert "hello" in clean


def test_sanitize_html():
    dirty = "<b>bold</b> <i>italic</i>"
    clean = sanitize_ui_input(dirty)
    assert "<" not in clean and ">" not in clean
    assert "bold" in clean and "italic" in clean


def test_sanitize_special_chars():
    dirty = "hello & goodbye < > \" ' /"
    clean = sanitize_ui_input(dirty)
    assert "<" not in clean and ">" not in clean
    assert "&" not in clean
    assert "hello" in clean and "goodbye" in clean


def test_sanitize_plain_text():
    text = "just a normal string!"
    assert sanitize_ui_input(text) == text
