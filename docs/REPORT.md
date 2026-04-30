# ACEest Fitness — DevOps CI/CD Implementation Report

**Student:** Atul Yadav  
**Roll Number:** 2024tm93580  
**Email:** 2024tm93580@wilp.bits-pilani.ac.in  
**Course:** Introduction to DEVOPS (CSIZG514 / SEZG514) — S1-25  
**Assignment:** 2 — DevOps CI/CD implementation for ACEest Fitness & Gym  
**Submission date:** 2026-04-30  
**GitHub repository:** https://github.com/atul411/devops-assignment-2

---

## 1. CI/CD Architecture Overview

The pipeline implements an industry-standard **build → test → quality-gate → image → deploy** flow with rollback capability at every layer.

```
GitHub  ──poll──►  Jenkins  ──►  flake8  ──►  pytest+cov  ──►  SonarQube QG
                                                                    │
                                                              docker build/push
                                                                    │
                                                              kubectl apply -k
                                                                    │
                                                              ┌─────┴─────┐
                                                              │  Rollout   │
                                                              │  Status    │
                                                              └─────┬─────┘
                                                                    │ on fail
                                                                    ▼
                                                          kubectl rollout undo
```

### Tool stack and rationale

| Concern | Tool | Why |
|---------|------|-----|
| Source control | **Git + GitHub** | Standard, free, integrates with Jenkins via webhooks/polling |
| Build server | **Jenkins (declarative pipeline)** | Mature, plugin-rich, on-prem friendly |
| Quality gate | **SonarQube** | Industry standard for Python static analysis + coverage gating |
| Containerisation | **Docker (multi-stage, slim base)** | Smaller images, reproducible runtime, non-root user |
| Registry | **Docker Hub** | Free for public images; tag policy `${BUILD_NUMBER}` + `latest` + semver |
| Orchestration | **Kubernetes (Minikube)** | Production-grade primitives for all 5 deployment strategies |
| Ingress | **nginx-ingress + (optionally) Istio** | nginx for canary/A/B, Istio for true Shadow mirroring |
| Tests | **pytest + pytest-cov** | Fast, parameterised, integrates with Sonar coverage reports |

### Application architecture

The Flask app exposes the same Tkinter domain (Fat Loss / Muscle Gain / Beginner programs, clients, weekly adherence, workouts, exercises, body metrics, role-based auth, AI-style program generator) as a RESTful + Jinja2 web service. A single Docker image runs as **v1 / v2 / v3** by toggling the `FEATURE_LEVEL` env var, which controls which Flask blueprints `create_app()` registers. This single-artifact-multi-config model is what makes Blue-Green and Canary meaningful: the same image is configured to behave as different versions, enabling safe cross-version traffic strategies.

---

## 2. Deployment Strategy Comparison

| Strategy | Rollback | User impact during deploy | Infra during cutover | Use case |
|----------|----------|--------------------------|---------------------|----------|
| **Rolling Update** | `kubectl rollout undo` (~2 min) | none if `maxUnavailable=0` | base + 1 surge pod | Default for safe, schema-compatible changes |
| **Blue-Green** | Service selector flip (~5 s) | none until flip | 2× pods during cutover | Risky migrations / instant rollback required |
| **Canary** | Re-annotate canary-weight to 0 | bounded by canary weight | base + 1 canary pod | Quantitative validation against real traffic |
| **Shadow** | Switch off mirror (instant) | zero (response discarded) | 2× compute (no ingress impact) | Side-effect-free perf / behaviour testing |
| **A/B Testing** | Per-cohort header drop | per-cohort | 2× pods | Compare cohort metrics across feature variants |

All five are implemented in `k8s/<strategy>/` and can be applied independently with `kubectl apply -k k8s/<strategy>/`.

---

## 3. Challenges Faced and Mitigation

| # | Challenge | Mitigation |
|---|-----------|------------|
| 1 | The supplied code was a **Tkinter desktop app**, but the assignment requires a **Flask web app**. Maintaining 3 separate Flask codebases (one per major version) would diverge quickly and triple the test/Docker burden. | Built a single Flask app with a `FEATURE_LEVEL` env var (1/2/3) that gates blueprint registration in the app factory. Same image, different runtime mode — production-grade pattern that powers all the K8s strategy demos. |
| 2 | **Shadow Deployment** has no native vanilla-K8s primitive. | Shipped an Istio `VirtualService` with `mirror` + `mirrorPercentage` (industry standard) **and** an nginx-ingress `mirror-target` annotation as a fallback for Minikube clusters without Istio. README explains the trade-offs. |
| 3 | **SQLite + ephemeral pods** would lose all client/workout data on restart, breaking deployment-strategy demos. | Mounted a `PersistentVolumeClaim` at `/data/aceest_fitness.db` in the base manifest. Documented that production should use Postgres/MySQL behind a managed service. |
| 4 | **SonarQube quality gate** would flag plaintext password storage as a Critical issue and fail the pipeline. | Stored the seeded admin password using `werkzeug.security.generate_password_hash(method="pbkdf2:sha256")`. Sonar exclusions configured for templates and `__init__.py`. |
| 5 | **Canary 75/25 by replica ratio** is non-deterministic — actual split varies with connection lifetime and load-balancer behaviour. | Used `nginx.ingress.kubernetes.io/canary-weight: "25"` annotation, which is deterministic at the request-routing layer. |
| 6 | **Liveness vs readiness** — a single `/health` would let pods receive traffic before SQLite was reachable. | Split into `/health` (process-up) and `/ready` (DB pingable). K8s probes wired to both with appropriate `initialDelaySeconds`. |
| 7 | **Pre-existing Tkinter dependency** (matplotlib, FPDF) was not assignment-relevant and would bloat image size. | Excluded from `requirements.txt`; only Flask + gunicorn + Werkzeug ship in the runtime image (slim base, ~75 MB compressed). |
| 8 | **Quality gate hangs forever if SonarQube is misconfigured.** | Wrapped `waitForQualityGate` in `timeout(5, MINUTES)` with `abortPipeline: true`. Pipeline aborts cleanly. |

---

## 4. Key Automation Outcomes

- **Zero-downtime deploys:** rolling update with `maxUnavailable=0` plus readiness probes guarantees no in-flight requests are dropped.
- **Single-step rollback:** every strategy has a documented one-command rollback (`kubectl rollout undo`, Service selector flip, or canary-weight back to 0).
- **Quality enforced at every commit:** flake8 + 48 pytest tests + SonarQube quality gate (≥80% line coverage, no critical/blocker issues) — a build cannot reach Docker Hub without passing all four. The SonarQube run executed during preparation **passed** the gate cleanly: 0 bugs, 0 vulnerabilities, 0 code smells, 80.9% coverage, all A ratings (see `docs/sonar-report/REPORT.md` for full results).
- **Deterministic image lineage:** image tags are `${BUILD_NUMBER}` + `latest` + git semver tag, so any deployed pod traces back to exactly one commit.
- **Self-contained reproducibility:** `make install && make test` and `docker-compose up -d --build` give a fresh contributor a working environment in under a minute. K8s strategies isolated to one folder each, applied with a single `kubectl apply -k`.
- **Defensive automation:** Jenkins post-failure block runs `kubectl rollout undo` automatically on `main` failures; HEALTHCHECK directive lets Docker mark unhealthy containers; PVC ensures state survives pod restarts.
- **Secure-by-default seeding:** the admin password seeds from `ADMIN_INITIAL_PASSWORD` env var; if absent, a random 16-character password is generated at first init and logged. SonarQube no longer flags hard-coded credentials.

---

## 5. Submission artefacts

| Artefact | Location |
|----------|----------|
| Flask application | `app/` (5 blueprints, 597 lines of code) |
| Pytest suite | `tests/` (48 tests, 80.9% coverage — verified by SonarQube) |
| Dockerfile | `Dockerfile` (multi-stage, slim, non-root, healthcheck) |
| Jenkinsfile | `Jenkinsfile` (declarative, polled SCM, quality gate, auto-rollback) |
| SonarQube config | `sonar-project.properties` |
| **SonarQube analysis report** | `docs/sonar-report/REPORT.md` + `results.json` (Quality Gate **PASSED**, 0 issues, all A ratings) |
| K8s manifests | `k8s/{base,rolling-update,blue-green,canary,shadow,ab-testing}/` |
| Helper scripts | `scripts/{bluegreen-switch,canary-promote,rollback}.sh` |
| GitHub Actions (secondary CI) | `.github/workflows/ci.yml` |
| Architecture diagram | `docs/architecture.md` |
| Submission checklist | `docs/SUBMISSION.md` |
| Deployment playbook | `docs/DEPLOYMENT.md` |

GitHub repository: **https://github.com/atul411/devops-assignment-2** (public)
Docker Hub: **https://hub.docker.com/r/atul411/aceest-fitness** (push triggered by `DOCKERHUB_TOKEN` secret in repo)
Cluster endpoint: see `docs/SUBMISSION.md` § 5 step 2 for spinning up a free-tier DigitalOcean K8s cluster (`kubectl get svc aceest-fitness -n aceest` → `EXTERNAL-IP`)
