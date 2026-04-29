"""Tests for envoy_sync.templater."""
import pytest
from envoy_sync.templater import render_template, RenderResult


def test_no_substitution_returns_values_unchanged():
    result = render_template({"KEY": "value", "OTHER": "plain"})
    assert result.rendered == {"KEY": "value", "OTHER": "plain"}
    assert result.is_complete


def test_dollar_brace_syntax_resolved_from_context():
    result = render_template({"URL": "https://${HOST}/api"}, context={"HOST": "example.com"})
    assert result.rendered["URL"] == "https://example.com/api"
    assert result.is_complete


def test_dollar_bare_syntax_resolved_from_context():
    result = render_template({"GREETING": "Hello $NAME"}, context={"NAME": "World"})
    assert result.rendered["GREETING"] == "Hello World"
    assert result.is_complete


def test_self_reference_within_template():
    template = {"BASE": "http://localhost", "URL": "${BASE}/path"}
    result = render_template(template)
    assert result.rendered["URL"] == "http://localhost/path"
    assert result.is_complete


def test_context_takes_precedence_over_self_reference():
    template = {"BASE": "http://localhost", "URL": "${BASE}/path"}
    result = render_template(template, context={"BASE": "https://prod.example.com"})
    assert result.rendered["URL"] == "https://prod.example.com/path"


def test_unresolved_variable_recorded():
    result = render_template({"DSN": "postgres://${DB_HOST}/db"})
    assert "DB_HOST" in result.unresolved
    assert not result.is_complete
    # Original placeholder preserved
    assert "${DB_HOST}" in result.rendered["DSN"]


def test_multiple_unresolved_variables_deduplicated():
    template = {"A": "$MISSING", "B": "$MISSING/extra"}
    result = render_template(template)
    assert result.unresolved.count("MISSING") == 1


def test_empty_template_returns_empty_result():
    result = render_template({})
    assert result.rendered == {}
    assert result.is_complete


def test_none_context_treated_as_empty():
    result = render_template({"X": "1"}, context=None)
    assert result.rendered == {"X": "1"}


def test_render_result_is_complete_false_when_unresolved():
    r = RenderResult(rendered={}, unresolved=["MISSING"])
    assert not r.is_complete


def test_render_result_is_complete_true_when_empty_unresolved():
    r = RenderResult(rendered={"K": "v"}, unresolved=[])
    assert r.is_complete
