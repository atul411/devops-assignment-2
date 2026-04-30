# SonarQube Analysis Report — ACEest Fitness

**Student**: Atul Yadav  
**Roll Number**: 2024tm93580  
**Email**: 2024tm93580@wilp.bits-pilani.ac.in  
**Course**: Introduction to DEVOPS (CSIZG514 / SEZG514) — S1-25  
**Assignment**: 2 — DevOps CI/CD implementation  
**GitHub repository**: https://github.com/atul411/devops-assignment-2

**Run timestamp**: 2026-04-30  
**Project**: aceest-fitness  
**Scanner**: sonarsource/sonar-scanner-cli (containerized)  
**Server**: SonarQube Community Edition 26.4

## Quality Gate

**Status: OK**

| Condition | Status | Actual | Threshold |
|-----------|--------|--------|-----------|
| new_coverage | OK | 83.7 | 80 |
| new_duplicated_lines_density | OK | 0.0 | 3 |
| new_violations | OK | 0 | 0 |

## Metrics Summary

| Metric | Value |
|--------|-------|
| Lines of code (non-comment) | 597 |
| Cyclomatic complexity | 125 |
| Cognitive complexity | 108 |
| Test coverage | 80.9% |
| Line coverage | 84.4% |
| Branch coverage | 66.7% |
| Duplicated lines % | 0.0% |
| Bugs | 0 |
| Vulnerabilities | 0 |
| Security hotspots (info) | 5 |
| Code smells | 0 |
| Reliability rating | 1.0 (A) |
| Security rating | 1.0 (A) |
| Maintainability (sqale) rating | 1.0 (A) |
| Technical debt (sqale_index, min) | 0 |

## Issues

Total open issues: **0**

No open issues at any severity.

## Security Hotspots (5 for review)

Hotspots are *informational* — they flag patterns that may need security review but are not necessarily issues. They do not block the quality gate.

| Status | Category | File | Line | Message |
|--------|----------|------|------|---------|
| TO_REVIEW | csrf | app/__init__.py | 8 | Make sure disabling CSRF protection is safe here. |
| TO_REVIEW | csrf | app/auth.py | 38 | Make sure allowing safe and unsafe HTTP methods is safe here. |
| TO_REVIEW | csrf | app/auth.py | 67 | Make sure allowing safe and unsafe HTTP methods is safe here. |
| TO_REVIEW | weak-cryptography | app/workouts.py | 138 | Make sure that using this pseudorandom number generator is safe here. |
| TO_REVIEW | weak-cryptography | app/workouts.py | 139 | Make sure that using this pseudorandom number generator is safe here. |

## How to reproduce

```bash
# Start SonarQube + scanner network
docker run -d --name sonarqube -p 9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community
docker network create sonarnet && docker network connect sonarnet sonarqube

# Run tests with coverage
pytest --cov=app --cov-report=xml:coverage.xml

# Run scanner (token from SonarQube UI: My Account -> Security)
docker run --rm --network sonarnet -v "$PWD:/usr/src" \
  -e SONAR_HOST_URL=http://sonarqube:9000 -e SONAR_TOKEN=$TOKEN \
  sonarsource/sonar-scanner-cli:latest
```
