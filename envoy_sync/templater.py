"""Template rendering for .env files using variable substitution."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class RenderResult:
    rendered: dict[str, str]
    unresolved: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return len(self.unresolved) == 0


def _resolve_value(
    value: str,
    env: dict[str, str],
    context: dict[str, str],
    missing: list[str],
) -> str:
    """Replace ${VAR} and $VAR references in *value* using env + context."""

    def replacer(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        if key in context:
            return context[key]
        if key in env:
            return env[key]
        if key not in missing:
            missing.append(key)
        return match.group(0)

    return _VAR_PATTERN.sub(replacer, value)


def render_template(
    template: dict[str, str],
    context: Optional[dict[str, str]] = None,
) -> RenderResult:
    """Render *template* by substituting variable references.

    Variables may reference other keys within the same template (resolved
    in iteration order) or keys supplied via *context*.

    Args:
        template: Mapping of env-var names to (possibly templated) values.
        context: Optional external values that take precedence over template
                 self-references.

    Returns:
        A :class:`RenderResult` with the rendered mapping and any keys that
        could not be resolved.
    """
    ctx: dict[str, str] = dict(context or {})
    rendered: dict[str, str] = {}
    unresolved: list[str] = []

    for key, value in template.items():
        resolved = _resolve_value(value, rendered, ctx, unresolved)
        rendered[key] = resolved

    return RenderResult(rendered=rendered, unresolved=sorted(set(unresolved)))
