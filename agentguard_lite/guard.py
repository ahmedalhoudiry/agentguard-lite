"""Default-deny tool dispatch with explicit host-side approval."""
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping


class Decision(str, Enum):
    ALLOW = 'allow'
    DENY = 'deny'
    APPROVAL_REQUIRED = 'approval_required'


class ToolDenied(PermissionError):
    pass


class ApprovalRequired(PermissionError):
    pass


@dataclass(frozen=True)
class Policy:
    allowed: frozenset[str] = field(default_factory=frozenset)
    approval_required: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        object.__setattr__(self, 'allowed', frozenset(self.allowed))
        object.__setattr__(self, 'approval_required', frozenset(self.approval_required))
        if not self.approval_required <= self.allowed:
            raise ValueError('Approval-required tools must also be allowed')

    def decide(self, tool: str) -> Decision:
        if tool not in self.allowed:
            return Decision.DENY
        if tool in self.approval_required:
            return Decision.APPROVAL_REQUIRED
        return Decision.ALLOW


class Guard:
    """Dispatch only registered, policy-approved tools.

    The approval callback belongs to the trusted host, never the agent.
    It must return the boolean True to authorize the current call.
    """
    def __init__(self, policy: Policy, tools: Mapping[str, Callable[..., Any]],
                 approve: Callable[[str, Mapping[str, Any]], bool] | None = None):
        self._policy = policy
        self._tools = MappingProxyType(dict(tools))
        self._approve = approve

    def call(self, tool: str, **kwargs: Any) -> Any:
        from copy import deepcopy
        if tool not in self._tools or self._policy.decide(tool) is Decision.DENY:
            raise ToolDenied(f'Tool not permitted: {tool}')
        if self._policy.decide(tool) is Decision.APPROVAL_REQUIRED:
            # Give the approver a separate copy so mutations cannot change execution.
            kwargs = deepcopy(kwargs)
            if self._approve is None or self._approve(tool, deepcopy(kwargs)) is not True:
                raise ApprovalRequired(f'Approval not granted: {tool}')
        return self._tools[tool](**kwargs)
