# Security Policy

Lysis is an open-source project that ranks GitHub issues for first-time contributors. We take security seriously, and we welcome responsible reports from researchers, contributors and users.

## Supported versions

| Version | Supported |
|---|---|
| `main` / latest release (what runs at trylysis.me) | Yes |
| Older releases and forks | No |

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report privately through GitHub: open the **Security** tab of this repository and click **Report a vulnerability**.

If that option is unavailable, email <help@trylysis.me> with:

- a description of the issue and its impact
- steps to reproduce, or a proof of concept
- the affected URL, endpoint, file or version

The URL or endpoint and a clear description are usually enough. Complex issues may need more detail.

## What to expect

- Acknowledgement within 7 days.
- An initial assessment within 14 days. We will share an expected resolution date when we can.
- Updates as we work on a fix. How long a fix takes depends on severity.
- Credit in the public advisory, unless you prefer to stay anonymous.
- If you follow this policy in good faith, we will not take legal action against you for the report.

We will keep your report and personal details confidential and will not share them without your permission.

## Scope

In scope:

- The web app at trylysis.me
- The API that serves it
- The code in this repository, including the GitHub Actions workflows
- Database access rules for the Supabase tables the app uses. For example, reading, changing or deleting another user's activity history through a missing or wrong Row Level Security policy is in scope.

Out of scope:

- Denial of service and volumetric attacks. The API is rate limited by design. Findings that show how to bypass the rate limiter are welcome, but please prove them with a handful of requests.
- Anything in third-party services (GitHub, Groq, Supabase, Render, Vercel). Please report those to the provider.
- The Supabase anon key and the analytics script being visible in the frontend. They are public by design and protected by Row Level Security.
- Attacks that require a man-in-the-middle position or physical access to a user's device.
- Clickjacking on pages with no sensitive actions, and unauthenticated logout or login CSRF.
- Content spoofing or text injection without a demonstrated way to modify HTML or CSS.
- Email spoofing, missing DNSSEC or CAA records, and cookie flags on non-sensitive cookies.
- Social engineering, physical attacks, spam and dead links.
- Output from automated scanners without a demonstrated impact.

## Testing rules

- Do not run automated scanners or load tests against production. If you want to test with tools, contact us and we will point you to a test target.
- Do not access, download, change or delete other people's data. Use your own account and the smallest proof you can.
- Please keep the issue private until it has been fixed. We will agree on a disclosure date with you..

## What we already do

- Input validation and per-IP rate limiting on the API.
- Row Level Security on every Supabase table.
- Security headers and an enforced Content Security Policy on the web app, and security headers on the API.
- Dependency monitoring with Dependabot and code scanning with CodeQL.
- Branch rules on `main` that require passing CI checks, including unit and browser tests.

## Handling secrets

Never include tokens, keys or personal data in a report, issue or pull request. If you find a leaked credential in this repository or its history, report it privately and we will rotate it.

## Questions

For general security questions that are not vulnerability reports, email <help@trylysis.me>.