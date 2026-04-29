"""Sort environment variable dictionaries by key or value."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortBy(str, Enum):
    KEY = "key"
    VALUE = "value"


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    order: SortOrder
    sort_by: SortBy

    @property
    def changed(self) -> bool:
        """Return True if the sort order differs from the original."""
        return list(self.original.keys()) != list(self.sorted_env.keys())

    @property
    def moved_keys(self) -> List[str]:
        """Return keys whose position changed after sorting."""
        orig_keys = list(self.original.keys())
        sorted_keys = list(self.sorted_env.keys())
        return [k for i, k in enumerate(sorted_keys) if orig_keys[i] != k]


def sort_env(
    env: Dict[str, str],
    order: SortOrder = SortOrder.ASC,
    sort_by: SortBy = SortBy.KEY,
    group_prefix: Optional[str] = None,
) -> SortResult:
    """Sort an env dict by key or value.

    If *group_prefix* is given, keys starting with that prefix are placed
    first (in their own sorted block) before the remaining keys.
    """
    reverse = order == SortOrder.DESC

    def _key_fn(item: tuple) -> str:
        return item[1] if sort_by == SortBy.VALUE else item[0]

    if group_prefix:
        prefixed = {k: v for k, v in env.items() if k.startswith(group_prefix)}
        rest = {k: v for k, v in env.items() if not k.startswith(group_prefix)}
        sorted_items = sorted(prefixed.items(), key=_key_fn, reverse=reverse)
        sorted_items += sorted(rest.items(), key=_key_fn, reverse=reverse)
    else:
        sorted_items = sorted(env.items(), key=_key_fn, reverse=reverse)

    sorted_env = dict(sorted_items)
    return SortResult(
        original=dict(env),
        sorted_env=sorted_env,
        order=order,
        sort_by=sort_by,
    )
