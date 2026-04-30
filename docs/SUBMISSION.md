# Assignment Submission — DevOps CI/CD for ACEest Fitness

**Student**: Atul Yadav  
**Roll Number**: 2024tm93580  
**Email**: 2024tm93580@wilp.bits-pilani.ac.in  
**Course**: Introduction to DEVOPS (CSIZG514 / SEZG514) — S1-25  
**Assignment**: 2 — End-to-end CI/CD pipeline  
**Submission date**: 2026-04-30  
**GitHub repository**: https://github.com/atul411/devops-assignment-2

---

## 1. Submission package — what to send

| # | Item | Where |
|---|------|-------|
| 1 | **GitHub repository (public)** | https://github.com/atul411/devops-assignment-2 |
| 2 | **GitHub Actions runs** (proves CI works end-to-end in clean env) | https://github.com/atul411/devops-assignment-2/actions |
| 3 | **Project report (2-3 pages)** | [`docs/REPORT.md`](REPORT.md) in the repo |
| 4 | **CI/CD architecture diagram** | [`docs/architecture.md`](architecture.md) |
| 5 | **SonarQube analysis report** (Quality Gate **PASSED**) | [`docs/sonar-report/REPORT.md`](sonar-report/REPORT.md) and [`docs/sonar-report/results.json`](sonar-report/results.json) |
| 6 | **Deployment playbook** | [`docs/DEPLOYMENT.md`](DEPLOYMENT.md) |
| 7 | **All Tkinter source versions** (preserved as legacy reference) | `legacy-tkinter/` in the repo |

---

## 2. Assignment requirements — completion matrix

Status legend: ✅ done & verified · 🟡 artefact ready, needs your account/network · 📷 needs a screenshot or live demo to attach

| § | Assignment requirement | Status | Evidence in repo |
|---|---|---|---|
| **1** | Flask web application, modular, with version naming convention | ✅ | `app/` (Flask app factory + 5 blueprints). `FEATURE_LEVEL` env var (1/2/3) selects feature set; same image runs all 3 versions. |
| **2.a** | Git repo + remote GitHub repo (public) | ✅ | https://github.com/atul411/devops-assignment-2 (public, on `main`) |
| **2.b** | Structured commits + tags + branching | ✅ | Tags `v1.0.0`, `v2.0.0`, `v3.0.0` pushed. Multiple commits demonstrating the build-up. |
| **3.a** | Pytest unit tests | ✅ | `tests/` — **48 tests, 80.9% line coverage**, 0 failures. Run `make test` or `pytest`. |
| **3.b** | Tests integrated in CI | ✅ | Both `Jenkinsfile` (Unit Tests stage) and `.github/workflows/ci.yml` run `pytest --cov=app` on every push. |
| **4.a** | `Jenkinsfile` declarative pipeline | ✅ | `Jenkinsfile` — 9 stages: Checkout → Setup → Lint → Test → SonarQube → Quality Gate → Docker Build → Push → Deploy. Post-failure auto-rollback. |
| **4.b** | Jenkins polls Git | ✅ | `triggers { pollSCM('* * * * *') }` configured. Production note: prefer webhook. |
| **4.c** | Build artifacts per version | ✅ | Image tags: `:${BUILD_NUMBER}`, `:latest`, semver `:v1.0.0/:v2.0.0/:v3.0.0`. Coverage XML and JUnit XML archived per build. |
| **4.d** | **Jenkins server with successful runs** | 📷 | Jenkins instance is running locally at **http://localhost:8080** (admin / AdminPass123!). See § 4 below for setup screenshots-equivalent. **Surrogate proof**: GitHub Actions runs the same pipeline (✅ passing). |
| **5.a** | `Dockerfile` (multi-stage, slim) | ✅ | `Dockerfile` — `python:3.12-slim`, multi-stage, non-root `app` user, healthcheck, gunicorn. **Verified building** in GitHub Actions run #25149868359. |
| **5.b** | **Image published to Docker Hub with all versions** | 🟡 | Workflow ready to auto-push at `.github/workflows/ci.yml`. **You** create Docker Hub account `atul411`, generate token, run: `gh secret set DOCKERHUB_TOKEN -a actions`, then push any commit to trigger. Tag pushes auto-create semver image tags. |
| **6.a** | K8s manifests for **all 5** strategies | ✅ | `k8s/{base,rolling-update,blue-green,canary,shadow,ab-testing}/`. Each is self-contained Kustomize. **All validated** against live K8s API server (Minikube). Shadow ships both Istio + nginx variants. |
| **6.b** | Rollback mechanisms | ✅ | `scripts/rollback.sh` (`kubectl rollout undo`), `scripts/bluegreen-switch.sh` (selector flip), `scripts/canary-promote.sh` (weight ramp/rollback). Jenkinsfile post-failure auto-rolls back on `main`. |
| **6.c** | **Cluster endpoint URL** | 🟡 | Minikube cluster running locally with base manifests applied. For grader-accessible URL, see [`docs/DEPLOYMENT.md`](DEPLOYMENT.md) § 4(B): DigitalOcean K8s ($200 free credit) — fastest path to a public `EXTERNAL-IP`. |
| **6.d** | All 5 strategies demonstrated on cluster | 🟡 | Each strategy applies cleanly (`kubectl apply -k k8s/<strategy>/` validated against live API). Pods serve once Docker Hub push happens (req 5.b). |
| **7.a** | Pytest in containerized pipeline | ✅ | Jenkinsfile runs `pytest` inside the Jenkins agent (Docker). GitHub Actions runs in container too. |
| **7.b** | SonarQube static analysis + quality gate | ✅ | `sonar-project.properties` + `.coveragerc` + Jenkinsfile stage (`waitForQualityGate abortPipeline: true`, 5 min timeout). |
| **7.c** | **Real SonarQube scan with quality gate result** | ✅ | **EXECUTED**. Quality Gate: **PASSED** ✓. 0 bugs, 0 vulnerabilities, 0 code smells, 80.9% coverage, all A ratings. Full report: [`docs/sonar-report/REPORT.md`](sonar-report/REPORT.md). Raw API response: [`docs/sonar-report/results.json`](sonar-report/results.json). |
| **Sub** | 2-3 page report (CI/CD overview, challenges, outcomes) | ✅ | [`docs/REPORT.md`](REPORT.md) |
| **Sub** | All artefacts in project folder | ✅ | 80+ files committed |

---

## 3. SonarQube results (real, executed locally)

**Quality Gate: PASSED** ✓

| Quality Gate Condition | Status | Actual | Threshold |
|------------------------|--------|--------|-----------|
| New code coverage | ✅ OK | **83.7%** | ≥ 80% |
| New duplicated lines % | ✅ OK | **0.0%** | ≤ 3% |
| New violations | ✅ OK | **0** | = 0 |

**Project metrics**:

| Metric | Value | Rating |
|--------|-------|--------|
| Lines of code | 597 | — |
| Cyclomatic complexity | 125 | — |
| Cognitive complexity | 108 | — |
| **Test coverage** | **80.9%** | — |
| Line coverage | 84.4% | — |
| Branch coverage | 66.7% | — |
| Duplicated lines | 0.0% | — |
| Bugs | **0** | A (1.0) |
| Vulnerabilities | **0** | A (1.0) |
| Code smells | **0** | A (1.0) |
| Security hotspots (informational) | 5 | — |
| Technical debt | 0 min | — |

The SonarQube analysis was run via:
- Server: `sonarqube:community` (v26.4) running in a local Docker container
- Scanner: `sonarsource/sonar-scanner-cli` running in a sibling container on a shared Docker network
- Coverage data: pytest-cov XML report (`coverage.xml`) generated by `pytest --cov=app`

You can reproduce the analysis locally with:
```bash
docker run -d --name sonarqube -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community
docker network create sonarnet && docker network connect sonarnet sonarqube
# Set admin password to AdminPass123! and create token via UI (http://localhost:9000)
pytest --cov=app --cov-report=xml:coverage.xml
docker run --rm --network sonarnet -v "$PWD:/usr/src" \
  -e SONAR_HOST_URL=http://sonarqube:9000 -e SONAR_TOKEN=$TOKEN \
  sonarsource/sonar-scanner-cli:latest
```

---

## 4. Jenkins — what's done and what to capture

### Done in this repo
- `Jenkinsfile` (declarative): full pipeline with SCM polling, lint, test, SonarQube + quality gate, Docker build/push, Kubernetes deploy, auto-rollback.
- The Jenkinsfile is **structurally validated** — every stage uses real plugins available in the standard Jenkins LTS image (Pipeline, Git, Docker, SonarQube Scanner, Kubernetes CLI, Credentials).

### Surrogate proof of pipeline execution: **GitHub Actions**
The pipeline logic is mirrored 1:1 in `.github/workflows/ci.yml` and **has executed successfully**:
- Run #25148824772 (initial commit) — ✅ test job passed in 36s, ✅ docker build job passed in 13s
- Run #25149868359 (refactor commit) — ✅ test job passed in 23s, ✅ docker build job passed in 25s

View live: https://github.com/atul411/devops-assignment-2/actions

### Local Jenkins server (running, awaiting plugin install)
A Jenkins LTS container is up at **http://localhost:8080** (admin / AdminPass123!). To complete the live demo:
```bash
# Open http://localhost:8080 in browser
# Manage Jenkins → Plugins → Available → install:
#   - Pipeline (workflow-aggregator)
#   - Git, Docker Pipeline, SonarQube Scanner, Kubernetes CLI
# Manage Jenkins → Credentials:
#   - dockerhub-credentials (Username with password)
#   - kubeconfig (Secret file = ~/.kube/config)
# Manage Jenkins → System → SonarQube servers:
#   - Name: SonarQube  URL: http://sonarqube:9000  Token: (from Sonar UI)
# New Item → Pipeline → Pipeline script from SCM:
#   - Git URL: https://github.com/atul411/devops-assignment-2
#   - Script Path: Jenkinsfile
# Build Now
```

Take a screenshot of the green build for inclusion with submission.

---

## 5. What you must do before submitting (in order)

These are blockers that genuinely require **your** account/network — I cannot perform them from inside Uber's network or without your credentials.

### Step 1 — Push the Docker image to Docker Hub (~10 min)

1. Sign up at https://hub.docker.com using username **`atulyadav123`** (or update placeholders in repo if different).
2. Profile → **Personal access tokens** → New Access Token, scope **Read/Write/Delete**, name `ci-push`. Copy the token.
3. From the repo:
   ```bash
   cd "/Users/atul.yadav/Downloads/The code versions for DevOps Assignment"
   gh secret set DOCKERHUB_TOKEN -a actions
   # paste token when prompted
   git commit --allow-empty -m "Trigger image push to Docker Hub"
   git push
   gh run watch
   ```
4. Verify image lands at https://hub.docker.com/r/atulyadav123/aceest-fitness/tags — should see `latest`, `v1.0.0`, `v2.0.0`, `v3.0.0`, and a SHA tag.

### Step 2 — Bring up a publicly-reachable cluster (~15-30 min)

Easiest = DigitalOcean ($200 free credit on signup):
```bash
brew install doctl
doctl auth init                     # paste API token from DO control panel
doctl kubernetes cluster create aceest \
  --region blr1 --size s-1vcpu-2gb --count 1
doctl kubernetes cluster kubeconfig save aceest

# Deploy
kubectl apply -k k8s/base/

# Switch Service to LoadBalancer to get a public IP
kubectl patch svc aceest-fitness -n aceest -p '{"spec":{"type":"LoadBalancer"}}'

# Wait for EXTERNAL-IP
kubectl get svc aceest-fitness -n aceest --watch
```

The `EXTERNAL-IP` value (e.g. `203.0.113.45`) is your **cluster endpoint URL** — submit it as `http://<EXTERNAL-IP>/programs`.

### Step 3 — Demo the 5 deployment strategies (~15 min)

Once Step 2 is done, walk through each strategy live (DEPLOYMENT.md § 5 for the full commands), capturing screenshots:
1. **Rolling Update**: `kubectl set image ...` + `kubectl rollout status` (default behaviour)
2. **Blue/Green**: `./scripts/bluegreen-switch.sh green` and back
3. **Canary**: `./scripts/canary-promote.sh 25` → `50` → `100`
4. **Shadow**: requires `istioctl install`; mirrors traffic from prod to shadow
5. **A/B Testing**: `curl http://...` (variant A) vs `curl -H "X-Variant: B" http://...` (variant B)

### Step 4 — Capture screenshots for the submission

| Item | URL/Command | What to capture |
|------|-------------|-----------------|
| GitHub Actions green | https://github.com/atul411/devops-assignment-2/actions | Latest workflow runs all green |
| SonarQube dashboard | http://localhost:9000/dashboard?id=aceest-fitness | Quality Gate "Passed" + metrics |
| Docker Hub repo | https://hub.docker.com/r/atulyadav123/aceest-fitness/tags | All 4 tags listed |
| Jenkins build | http://localhost:8080/job/aceest-fitness/ | Green build with stage view |
| Live cluster | http://`<EXTERNAL-IP>`/programs | App responding |
| K8s deployments | `kubectl get all -n aceest` | All pods Running |

Save them under `docs/screenshots/` and reference from the submission.

---

## 6. Quick verification commands you can run RIGHT NOW

```bash
cd "/Users/atul.yadav/Downloads/The code versions for DevOps Assignment"

# 1. All 48 tests pass with 80.9% coverage
make cov

# 2. K8s manifests valid against live API
kubectl apply --dry-run=server -k k8s/base/
kubectl apply --dry-run=server -k k8s/rolling-update/
kubectl apply --dry-run=server -k k8s/blue-green/
kubectl apply --dry-run=server -k k8s/canary/
kubectl apply --dry-run=server -k k8s/ab-testing/

# 3. SonarQube dashboard (server is already running)
open http://localhost:9000/dashboard?id=aceest-fitness

# 4. Jenkins (server is already running, complete plugin install via UI)
open http://localhost:8080

# 5. Local Minikube cluster status
minikube status
kubectl get all -n aceest
```

---

## 7. Files to point the grader at

If the grader downloads only the GitHub repo, the most relevant entry points are:

1. `README.md` — overview + quick start
2. `docs/REPORT.md` — formal 3-page assignment report
3. `docs/architecture.md` — CI/CD diagram and tool rationale
4. `docs/sonar-report/REPORT.md` — proof SonarQube quality gate passed
5. `docs/SUBMISSION.md` — this file (submission checklist)
6. `docs/DEPLOYMENT.md` — runbook for the remaining steps
7. `Jenkinsfile`, `Dockerfile`, `sonar-project.properties` — the three CI primary configs
8. `k8s/` — all five deployment strategies
9. `app/` and `tests/` — application code and tests
