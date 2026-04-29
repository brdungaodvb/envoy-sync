"""Tests for envoy_sync.redactor."""

import pytest

from envoy_sync.redactor import (
    REDACTED_PLACEHOLDER,
    RedactionResult,
    is_sensitive_key,
    redact_env,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "PASSWORD", "DB_PASSWORD", "password",
    "SECRET", "APP_SECRET_KEY",
    "API_KEY", "APIKEY",
    "AUTH_TOKEN", "OAUTH_TOKEN",
    "PRIVATE_KEY", "PRIVATE_KEY_PEM",
    "AWS_SECRET_ACCESS_KEY",
    "CREDENTIALS",
])
def test_sensitive_keys_are_detected(key):
    assert is_sensitive_key(key) is True


@pytest.mark.parametrize("key", [
    "HOST", "PORT", "DEBUG", "APP_NAME", "LOG_LEVEL", "DATABASE_URL",
])
def test_non_sensitive_keys_are_not_detected(key):
    assert is_sensitive_key(key) is False


def test_custom_pattern_matches():
    assert is_sensitive_key("MY_PIN", patterns=[r"(?i)pin"]) is True


def test_custom_pattern_does_not_match_default_sensitive():
    # Only custom pattern supplied — default patterns NOT used
    assert is_sensitive_key("DB_PASSWORD", patterns=[r"(?i)pin"]) is False


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_replaces_sensitive_values():
    env = {"DB_PASSWORD": "s3cr3t", "HOST": "localhost"}
    result = redact_env(env)
    assert result.redacted["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result.redacted["HOST"] == "localhost"


def test_redact_original_is_unchanged():
    env = {"API_KEY": "abc123", "PORT": "8080"}
    result = redact_env(env)
    assert result.original["API_KEY"] == "abc123"


def test_redacted_keys_list_is_sorted():
    env = {"TOKEN": "t", "SECRET": "s", "HOST": "h"}
    result = redact_env(env)
    assert result.redacted_keys == sorted(result.redacted_keys)


def test_redaction_count():
    env = {"API_KEY": "k", "PASSWORD": "p", "HOST": "h", "PORT": "80"}
    result = redact_env(env)
    assert result.redaction_count == 2


def test_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    assert result.redaction_count == 0
    assert result.redacted == env


def test_empty_env():
    result = redact_env({})
    assert result.redacted == {}
    assert result.redacted_keys == []


def test_custom_placeholder():
    env = {"DB_PASSWORD": "secret"}
    result = redact_env(env, placeholder="<hidden>")
    assert result.redacted["DB_PASSWORD"] == "<hidden>"


def test_result_is_redaction_result_instance():
    result = redact_env({"KEY": "val"})
    assert isinstance(result, RedactionResult)
