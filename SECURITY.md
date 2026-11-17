# Security Policy

Lysis is an early prototype (v0.1). Security reports are welcome and taken seriously.

## Supported versions

| Version | Supported |
|---|---|
| main / latest release | Yes |
| older releases | No |

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report privately through GitHub: open the Security tab of this repository and click **Report a vulnerability**.

If that option is unavailable, email <hvora@umassd.edu> with:

- a description of the issue and its impact
- steps to reproduce
- affected endpoint, file or version

## What to expect

- Acknowledgement within 7 days.
- An initial assessment within 14 days.
- Fix or mitigation timing depends on severity. Reporters are credited unless they prefer otherwise.

## Scope

In scope: the API, the web frontend, and the code in this repository.

Out of scope: denial-of-service through volume (the API is rate-limited by design), and issues in third-party services (GitHub, Groq, Supabase, Render, Vercel). Report those to the provider.

## Handling secrets

Never include tokens or keys in a report, issue or pull request. If you find a leaked credential in this repository, report it privately and it will be rotated.