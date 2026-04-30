"""Tests for envoy_sync.linter."""
import pytest
from envoy_sync.linter import lint_env, LintResult


def test_clean_env_returns_no_issues():
    result = lint_env({"HOST": "localhost", "PORT": "8080"})
    assert result.is_clean


def test_empty_value_produces_warning():
    result = lint_env({"HOST": ""})
    assert not result.errors
    assert any("empty value" in w for w in result.warnings)


def test_lowercase_key_produces_warning():
    result = lint_env({"host": "localhost"})
    assert any("not uppercase" in w for w in result.warnings)


def test_key_with_space_produces_error():
    result = lint_env({"MY KEY": "value"})
    assert any("contains a space" in e for e in result.errors)


def test_very_long_value_produces_warning():
    result = lint_env({"SECRET": "x" * 600})
    assert any("very long value" in w for w in result.warnings)


def test_duplicate_key_in_raw_lines_produces_error():
    lines = ["HOST=localhost\n", "PORT=8080\n", "HOST=remotehost\n"]
    result = lint_env({"HOST": "remotehost", "PORT": "8080"}, raw_lines=lines)
    assert any("Duplicate key 'HOST'" in e for e in result.errors)


def test_trailing_whitespace_in_raw_lines_produces_warning():
    lines = ["HOST=localhost   \n"]
    result = lint_env({"HOST": "localhost"}, raw_lines=lines)
    assert any("trailing whitespace" in w for w in result.warnings)


def test_crlf_line_ending_produces_warning():
    lines = ["HOST=localhost\r\n"]
    result = lint_env({"HOST": "localhost"}, raw_lines=lines)
    assert any("CRLF" in w for w in result.warnings)


def test_summary_clean():
    result = LintResult()
    assert result.summary() == "No lint issues found."


def test_summary_contains_errors_and_warnings():
    result = LintResult(warnings=["watch out"], errors=["bad key"])
    summary = result.summary()
    assert "[error]" in summary
    assert "[warning]" in summary
    assert "bad key" in summary
    assert "watch out" in summary


def test_is_clean_false_with_warnings():
    result = LintResult(warnings=["something"])
    assert not result.is_clean


def test_is_clean_false_with_errors():
    result = LintResult(errors=["bad"])
    assert not result.is_clean


def test_blank_and_comment_lines_skipped_for_duplicate_check():
    lines = ["# comment\n", "\n", "HOST=localhost\n"]
    result = lint_env({"HOST": "localhost"}, raw_lines=lines)
    assert result.is_clean
