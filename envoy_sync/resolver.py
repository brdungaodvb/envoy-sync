"""Resolve merge sources from file paths and produce a merged env dict."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envoy_sync.merger import MergeStrategy, merge_envs
from envoy_sync.parser import parse_env_file


def resolve_files(
    paths: List[str | Path],
    strategy: MergeStrategy = MergeStrategy.LAST,
    encoding: str = "utf-8",
) -> Dict[str, str]:
    """Parse each .env file and merge them into a single mapping.

    Parameters
    ----------
    paths:
        Ordered list of file paths to load.
    strategy:
        Conflict resolution strategy passed to :func:`merge_envs`.
    encoding:
        File encoding (default: utf-8).

    Returns
    -------
    dict
        Merged environment variables.

    Raises
    ------
    FileNotFoundError
        If any of the given paths does not exist.
    """
    sources = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"env file not found: {path}")
        env = parse_env_file(path, encoding=encoding)
        sources.append((str(path), env))

    return merge_envs(sources, strategy=strategy)


def resolve_with_overrides(
    base_path: str | Path,
    override_path: Optional[str | Path] = None,
    strategy: MergeStrategy = MergeStrategy.LAST,
) -> Dict[str, str]:
    """Convenience helper: load a base file and an optional override file.

    The override file (e.g. ``.env.local``) is applied on top of the base
    using the given *strategy*.
    """
    paths: List[str | Path] = [base_path]
    if override_path is not None:
        paths.append(override_path)
    return resolve_files(paths, strategy=strategy)
