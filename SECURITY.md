Security remediation steps

1) Remove secrets from history
- Use scripts/purge_secrets_history.sh to remove literals and .env from git history (requires git-filter-repo).

2) Rotate compromised credentials
- Rotate MongoDB user/password, regenerate API keys (OpenAI/Gemini).
- Revoke old JWT secrets and set a new SECRET_KEY in GitHub Actions and hosting envs.

3) Add secrets to GitHub
- Store keys in repository secrets (Settings > Secrets) and reference them in CI.

4) Use strong JWT strategy
- Short-lived access tokens, refresh tokens stored server-side and revocable (implemented).

5) Dependency scanning
- CI runs pip-audit and npm audit; act on high/critical findings.

6) Monitoring
- Enable secret scanning in GitHub and alerting for pushes.
