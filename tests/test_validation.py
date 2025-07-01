from ui.input_validation import validate_ui_input


def test_validate_text():
    assert validate_ui_input("Hello world!", "text")[0]
    assert not validate_ui_input("", "text")[0]
    assert not validate_ui_input("A" * 1001, "text")[0]


def test_validate_email():
    assert validate_ui_input("user@example.com", "email")[0]
    assert not validate_ui_input("user@", "email")[0]


def test_validate_username():
    assert validate_ui_input("user_123", "username")[0]
    assert not validate_ui_input("us", "username")[0]
    assert not validate_ui_input("user!@#", "username")[0]


def test_validate_password():
    assert validate_ui_input("Passw0rd!", "password")[0]
    assert not validate_ui_input("password", "password")[0]
    assert not validate_ui_input("12345678", "password")[0]


def test_validate_url():
    assert validate_ui_input("https://example.com", "url")[0]
    assert not validate_ui_input("htp:/bad", "url")[0]


def test_validate_filepath():
    assert validate_ui_input("/tmp/file.txt", "filepath")[0]
    assert not validate_ui_input("", "filepath")[0]


def test_validate_alphanumeric():
    assert validate_ui_input("abc123", "alphanumeric")[0]
    assert not validate_ui_input("abc 123!", "alphanumeric")[0]


def test_invalid_type():
    valid, msg = validate_ui_input("test", "unknown_type")
    assert not valid
    assert "Invalid input type" in msg
