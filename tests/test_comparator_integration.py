"""Integration tests combining parser + comparator."""
from envoy_sync.parser import parse_env_file
from envoy_sync.comparator import compare_envs


BEFORE = """\
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
SECRET_KEY=abc123
"""

AFTER = """\
DB_HOST=prod.example.com
DB_PORT=5432
DB_NAME=mydb
SECRET_KEY=xyz789
NEW_FEATURE=enabled
"""


def test_real_env_strings_produce_correct_report():
    before = parse_env_file(BEFORE)
    after = parse_env_file(AFTER)
    report = compare_envs(before, after)

    assert report.has_changes
    assert "NEW_FEATURE" in report.added
    assert report.added["NEW_FEATURE"] == "enabled"
    assert "DB_HOST" in [k for k, _, _ in report.modified]
    assert "SECRET_KEY" in [k for k, _, _ in report.modified]
    assert not report.removed
    assert "DB_PORT" in report.unchanged
    assert "DB_NAME" in report.unchanged


def test_round_trip_identical_parse():
    env = parse_env_file(BEFORE)
    report = compare_envs(env, env.copy())
    assert not report.has_changes
    assert len(report.unchanged) == len(env)


def test_summary_output_is_human_readable():
    before = parse_env_file(BEFORE)
    after = parse_env_file(AFTER)
    report = compare_envs(before, after)
    summary = report.summary()
    assert "added" in summary
    assert "modified" in summary
    assert "NEW_FEATURE" in summary
