# AgentGuard Lite

A small, dependency-free Python prototype for enforcing tool-call permissions in AI agent applications. It separates policy decisions from tool implementation and lets the trusted host request approval for sensitive calls.

**Status:** early-stage prototype (0.1.0). Not a production security boundary. No adoption or external contributor metrics are claimed.

## Features

- Default-deny allowlist for registered tools.
- Explicit approval callback for sensitive tools.
- Immutable policy sets; no model or vendor SDK required.
- Standard-library unit tests and a local interactive example.

## Installation

Requires Python 3.10+. From this repository:

```sh
python -m pip install .
```

## Quick start

```python
from agentguard_lite import Guard, Policy

policy = Policy(allowed={'read_note', 'send_message'},
                approval_required={'send_message'})
guard = Guard(policy, {'read_note': lambda: 'hello',
                       'send_message': lambda message: message})
print(guard.call('read_note'))
# guard.call('send_message', message='hello') raises ApprovalRequired.
```

The host can provide an `approve(tool, arguments)` callback that returns exactly `True` after authenticating and obtaining approval from a human. Do not give the model control over the callback, registry, policy, or access to raw tools. For this prototype, pass ordinary JSON-compatible arguments only.

Run the local example after installation:

```sh
python examples/basic.py
python -m unittest discover -s tests -v
```

## Threat model and limitations

The gate checks tool names, not the semantic safety of arguments or tool implementations. It is not a sandbox and does not prevent prompt injection, enforce per-user identity, validate schemas, provide persistent audit logs, or isolate processes. Every call must pass through the trusted dispatcher. The approval callback must be implemented securely by the host; this prototype does not provide durable approval records or remote authentication. Approved tools can still fail or cause harm; apply least privilege outside this library as well.

## Roadmap

- Argument-level validation and policy constraints.
- Structured, privacy-conscious decision logging.
- Adapters for common agent frameworks.
- More integration tests and independent review.

Contributions and reproducible bug reports are welcome. See CONTRIBUTING.md and SECURITY.md. Licensed under MIT.
