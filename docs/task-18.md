# Task 18: Security and Code Quality
- Secrets and environment settings are in .env, and production-only security settings switch on when DEBUG=False.
- Ran the deployment check, a code search for raw SQL and unsafe output, ruff (unused imports) and pip-audit. Results are in docs/security-review.md.
- Added tests for CSRF, session cookies, private fields in the API and safe error pages.
- Errors and fixes: replaced the insecure secret key and moved ALLOWED_HOSTS into .env.