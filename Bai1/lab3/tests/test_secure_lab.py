import json
import logging

from securelogger.logger import JSONFormatter, get_secure_logger, mask_pii
from securevalidator.core import (
    sanitize_html_input,
    sanitize_sql_input,
    validate_email,
    validate_filename,
    validate_url,
)


def test_validate_email_ok():
    assert validate_email("student@example.com") is True
    assert validate_email("name.surname@domain.edu.vn") is True


def test_validate_email_invalid():
    assert validate_email("not-an-email") is False
    assert validate_email("@example.com") is False


def test_validate_url_ok():
    assert validate_url("https://example.com") is True
    assert validate_url("http://localhost:5000") is True


def test_validate_url_invalid():
    assert validate_url("ftp://example.com") is False
    assert validate_url("example.com") is False
    assert validate_url("") is False


def test_validate_filename_ok():
    assert validate_filename("report.txt") is True
    assert validate_filename("image_01.png") is True


def test_validate_filename_invalid():
    assert validate_filename("../etc/passwd") is False
    assert validate_filename("folder/report.txt") is False
    assert validate_filename("..\\secret.txt") is False


def test_sanitize_sql_input_removes_dangerous_tokens():
    raw = "SELECT * FROM users WHERE name = 'admin'; DROP TABLE users;"
    cleaned = sanitize_sql_input(raw)
    assert "SELECT" not in cleaned.upper()
    assert "DROP" not in cleaned.upper()
    assert ";" not in cleaned
    assert "admin" in cleaned
    assert "name =" in cleaned


def test_sanitize_html_input_escapes_html():
    raw = "<script>alert('x')</script>"
    cleaned = sanitize_html_input(raw)
    assert "&lt;script&gt;" in cleaned
    assert "<script>" not in cleaned


def test_mask_pii_masks_email_and_token():
    text = "Email: user@example.com and token=abcd1234efgh"
    masked = mask_pii(text)
    assert "<email_masked>" in masked
    assert "<token_masked>" in masked


def test_json_formatter_masks_sensitive_fields():
    record = logging.LogRecord(
        name="secure_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Email is user@example.com and token=abcd1234efgh",
        args=(),
        exc_info=None,
    )
    record.data = {"email": "user@example.com"}
    record.results = {"email": "user@example.com", "sql": "SELECT * FROM users"}

    formatted = JSONFormatter().format(record)
    payload = json.loads(formatted)

    assert payload["level"] == "INFO"
    assert "<email_masked>" in payload["message"]
    assert "<token_masked>" in payload["message"]
    assert payload["data"]["email"] == "<email_masked>"
    assert payload["results"]["email"] == "<email_masked>"


def test_get_secure_logger_creates_logger_with_handler():
    logger = get_secure_logger()
    assert logger.name == "secure_logger"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1
    assert logger.propagate is False
