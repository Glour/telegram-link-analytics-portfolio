# Link analytics: code sample

A focused portfolio extract adapted from a larger Telegram campaign application. It illustrates destination validation, request classification, pseudonymous daily visitor identifiers and a React statistics view. This is a code sample, not a deployable tracking service: persistence, authentication, HTTP routing, cookie handling and production configuration are outside its scope.

## Structure

- `src/link_analytics/domain.py` — framework-independent domain logic and metric invariants.
- `tests/test_domain.py` — unit tests for URL safety, classification, token integrity and metrics.
- `frontend/LinkMetrics.tsx` — typed, presentation-only React component; a host application supplies data and React dependencies.

## Run the tests

Python 3.9 or newer; no third-party packages are needed:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Design notes

The destination allowlist rejects credentials, ports, control characters and non-Telegram hosts. Requests are classified using simple heuristics: a transition is not proof of a human or subscription. A signed random browser token can be used to produce a day-scoped HMAC identifier; an integrating application must use a securely managed secret and set appropriate cookie attributes. Daily unique counts summed across days are estimates, not distinct people over the whole period. Operational privacy measures, retention and a security review remain necessary before deployment.

## Provenance

Adapted and refactored from an existing application with AI-assisted development. This repository is a curated code sample and does not claim to represent the entire original product or an independently audited production system.
