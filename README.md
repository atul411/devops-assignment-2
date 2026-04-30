# ACEest Fitness & Gym — DevOps CI/CD

**Student**: Atul Yadav  
**Roll Number**: 2024tm93580  
**Email**: 2024tm93580@wilp.bits-pilani.ac.in  
**Course**: Introduction to DEVOPS (CSIZG514 / SEZG514) — S1-25 · **Assignment 2**  
**GitHub**: https://github.com/atul411/devops-assignment-2

A Flask-based fitness management application with a complete CI/CD pipeline implementation for the **Introduction to DEVOPS (CSIZG514/SEZG514)** Assignment 2.

The original assignment provided a Tkinter desktop app across 10 incremental versions; this repository ports the domain (programs, clients, workouts, progress) into a Flask web service and wraps it in a fully automated DevOps pipeline.

## Quick start

```bash
# Local dev
make install
make test           # 48 pytest tests, ~80% coverage
make run            # http://localhost:5000

# Containerised
docker-compose up -d --build

# Kubernetes (Minikube)
kubectl apply -k k8s/base/                 # baseline (Rolling Update default)
kubectl apply -k k8s/blue-green/           # OR Blue-Green
kubectl apply -k k8s/canary/               # OR Canary
kubectl apply -k k8s/shadow/               # OR Shadow (Istio)
kubectl apply -k k8s/ab-testing/           # OR A/B Testing
```

## Application versions

The same Docker image runs as v1 / v2 / v3 by toggling `FEATURE_LEVEL` (1, 2, or 3):

| Level | Routes registered | Mirrors Tkinter |
|-------|-------------------|-----------------|
| 1 | `/programs` (read-only program info) | `Aceestver-1.0.py` |
| 2 | + `/clients` CRUD + progress tracking | `Aceestver-2.x.py` |
| 3 | + `/login`, `/workouts`, `/metrics`, `/program-generator`, `/dashboard` | `Aceestver-3.x.py` |

Default admin user: **admin / admin** (password is hashed with PBKDF2-SHA256).

## API surface (FEATURE_LEVEL=3)

| Method | Path | Notes |
|--------|------|-------|
| GET | `/health` | Liveness — always 200 |
| GET | `/ready` | Readiness — pings SQLite |
| GET | `/programs` | HTML or `?format=json` |
| GET | `/programs/<key>` | `FL`, `MG`, `BG` |
| GET | `/programs/<key>/calories?weight=70` | Calorie calc (factor × weight) |
| GET / POST | `/clients/` | List / create |
| GET / PATCH / DELETE | `/clients/<name>` | Detail / update / delete |
| GET / POST | `/clients/<name>/progress` | Weekly adherence log |
| POST | `/login` / `/logout` | Session-based auth |
| GET / POST | `/workouts/<name>` | Workouts per client |
| POST | `/workouts/<id>/exercises` | Exercise sets/reps/weight |
| GET / POST | `/metrics/<name>` | Body weight / waist / bodyfat |
| POST | `/program-generator/<name>` | Random AI-style program |

## DevOps pipeline

```
Developer push -> GitHub
         |
         v
  Jenkins (pollSCM 1m) ---> Checkout -> Setup -> Lint (flake8) -> Pytest (--cov)
                                                                   |
                                                                   v
                                                 SonarQube scan -> Quality Gate (fail = abort)
                                                                                |
                                                                                v
                                                            docker build -> docker push
                                                                                |
                                                                                v
                                                               kubectl apply -k k8s/<strategy>/
                                                                                |
                                                                                v
                                                                  Deployment health check
                                                                  (auto-rollback on failure)
```

See [docs/architecture.md](docs/architecture.md) for the full diagram and [docs/REPORT.md](docs/REPORT.md) for the 2-page report.

## Repository layout

```
app/                Flask application (factory + 5 blueprints)
tests/              Pytest suite (48 tests, ≥80% coverage)
k8s/                Kubernetes manifests
  base/             Namespace + ConfigMap + Secret + PVC + Deployment + Service + Ingress
  rolling-update/   Default RollingUpdate (maxSurge=1, maxUnavailable=0)
  blue-green/       Two Deployments + Service selector switch
  canary/           Stable + canary, nginx-ingress canary-weight
  shadow/           Istio VirtualService.mirror (+ nginx fallback)
  ab-testing/       Two variants, header-routed via X-Variant: B
scripts/            bluegreen-switch.sh, canary-promote.sh, rollback.sh
docs/               REPORT.md (assignment write-up), architecture.md
legacy-tkinter/     Original Tkinter sources preserved for reference
Dockerfile          Multi-stage, python:3.12-slim, gunicorn, non-root, healthcheck
Jenkinsfile         Declarative pipeline with SonarQube quality gate
sonar-project.properties
.github/workflows/  Optional GitHub Actions secondary CI
docker-compose.yml  Local dev with persistent SQLite volume
Makefile            Common dev tasks
```

## Configured identifiers

This repo is pre-configured for the following identities — replace if you fork:

| Identifier | Value | Used in |
|------------|-------|---------|
| GitHub repo | `atul411/devops-assignment-2` | Dockerfile LABEL, README links |
| Docker Hub repo | `atulyadav123/aceest-fitness` | Dockerfile, Jenkinsfile, all `k8s/*/*.yaml` |
| Jenkins credential ID | `dockerhub-credentials` | `Jenkinsfile` (configure under Jenkins → Credentials) |
| Jenkins credential ID | `kubeconfig` | `Jenkinsfile` (kubeconfig file credential) |
| Ingress hostname | `aceest.local` | All `k8s/**/ingress*.yaml` (replace with your real hostname) |

## Submission checklist

- [x] Flask app + 3 versions (single image, FEATURE_LEVEL toggle)
- [x] Pytest suite (48 tests, 80.9% coverage)
- [x] Dockerfile (multi-stage, non-root, healthcheck) — verified via GitHub Actions
- [x] Jenkinsfile (declarative, pollSCM, SonarQube quality gate, auto-rollback)
- [x] Kubernetes manifests for all 5 deployment strategies — validated against live API
- [x] **SonarQube analysis executed — Quality Gate PASSED** (0 bugs, 0 vulns, 0 smells, all A ratings)
- [x] Rollback scripts (bluegreen-switch, canary-promote, rollback)
- [x] 2-3 page report ([docs/REPORT.md](docs/REPORT.md))
- [x] Submission checklist ([docs/SUBMISSION.md](docs/SUBMISSION.md))
- [x] Deployment playbook ([docs/DEPLOYMENT.md](docs/DEPLOYMENT.md))
- [x] **GitHub repo public** at https://github.com/atul411/devops-assignment-2
- [x] GitHub Actions runs green
- [ ] Docker Hub push (needs your `DOCKERHUB_TOKEN` secret — workflow auto-pushes once set)
- [ ] Public cluster endpoint (needs cloud K8s — see DEPLOYMENT.md § 4(B))
- [ ] Live Jenkins build screenshot (Jenkins is running locally; complete plugin install via UI)
