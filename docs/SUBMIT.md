# 📦 How to submit this assignment — final guide

**Student**: Atul Yadav  
**Roll Number**: 2024tm93580  
**Email**: 2024tm93580@wilp.bits-pilani.ac.in  
**Course**: Introduction to DEVOPS (CSIZG514 / SEZG514) — S1-25  
**Assignment**: 2 — DevOps CI/CD implementation for ACEest Fitness & Gym  
**GitHub repository**: https://github.com/atul411/devops-assignment-2

This is the single document you need to follow to submit Assignment 2 (DevOps CI/CD for ACEest Fitness).

---

## 🎯 TL;DR — submit these THREE things

1. **GitHub repository URL** (public): `https://github.com/atul411/devops-assignment-2`
2. **PDF report** — convert `docs/REPORT.md` → PDF (instructions below) and upload to LMS
3. **Cluster endpoint URL** — once you complete the cloud-K8s step (§ 3 below)

If your LMS also requires a project ZIP, use `submission/devops-assignment-2.zip` (auto-generated, see § 4).

---

## 1. What's already done — copy these URLs into your submission

| Required by assignment | URL / Location |
|------------------------|----------------|
| GitHub repo (public) | https://github.com/atul411/devops-assignment-2 |
| GitHub Actions runs (CI proof) | https://github.com/atul411/devops-assignment-2/actions |
| Tags v1.0.0 / v2.0.0 / v3.0.0 | https://github.com/atul411/devops-assignment-2/tags |
| Project report (2-3 pages) | `docs/REPORT.md` in the repo (or PDF — see § 2) |
| CI/CD architecture diagram | `docs/architecture.md` |
| **SonarQube analysis (Quality Gate PASSED)** | `docs/sonar-report/REPORT.md` + `docs/sonar-report/results.json` |
| Pytest test cases | `tests/` (48 tests, 80.9% line coverage) |
| Jenkinsfile | `Jenkinsfile` (declarative, 9 stages) |
| Dockerfile | `Dockerfile` (multi-stage, slim, non-root) |
| K8s manifests for all 5 strategies | `k8s/{base,rolling-update,blue-green,canary,shadow,ab-testing}/` |

---

## 2. Generate the submission PDF (5 sec)

Some LMS systems want a single PDF report. The repo has three pre-built PDFs ready in `submission/` after running `make pdf`:

```bash
cd "/Users/atul.yadav/Downloads/The code versions for DevOps Assignment"
make pdf       # generates submission/REPORT.pdf, SUBMIT.pdf, sonar-REPORT.pdf
ls submission/*.pdf
```

`make pdf` auto-detects what's available on your machine:
1. **Google Chrome headless** (preferred — no extra install needed; uses your existing Chrome)
2. **pandoc + pdflatex** (fallback if Chrome not at `/Applications/Google Chrome.app`)

If neither works, fall back to HTML:

```bash
make html      # generates submission/*.html
open submission/REPORT.html
# In browser: ⌘P → Save as PDF
```

Or use any online markdown→PDF converter like https://md2pdf.netlify.app.

---

## 3. The THREE things ONLY YOU can do (need your accounts)

These cannot be automated from inside your work network or without your personal accounts.

### Step 1 — Push image to Docker Hub (10 min)

The assignment requires "your own docker image-repo with all versions of the application". Do this:

1. Sign up at https://hub.docker.com using username **`atul411`**.
2. After login → **Account Settings** → **Personal access tokens** → **Generate new token**.
   - Token name: `ci-push`
   - Expiration: 90 days (or no expiry)
   - Permission: **Read, Write, Delete**
   - Click **Generate** → **copy the token now** (it's shown only once).
3. From the project folder:
   ```bash
   cd "/Users/atul.yadav/Downloads/The code versions for DevOps Assignment"
   gh secret set DOCKERHUB_TOKEN -a actions
   # paste the token when prompted
   git commit --allow-empty -m "Trigger image push to Docker Hub"
   git push
   gh run watch
   ```
4. After the workflow completes (~1 min), confirm at:
   https://hub.docker.com/r/atul411/aceest-fitness/tags
   — you should see `latest`, `v1.0.0`, `v2.0.0`, `v3.0.0`, and a SHA tag.
5. **Copy this URL into your submission**: `https://hub.docker.com/r/atul411/aceest-fitness`

### Step 2 — Spin up a public-IP Kubernetes cluster (15-30 min)

The assignment requires "the endpoint URL of your running cluster". Local Minikube isn't reachable by graders — you need cloud K8s.

**Easiest option: DigitalOcean** ($200 free credit on signup, no permanent free tier but plenty for a demo)

```bash
# 1. Sign up at https://cloud.digitalocean.com  (use the $200 credit link from BITS or any signup bonus)
# 2. Generate an API token: API → Tokens/Keys → Generate New Token (Read+Write)

brew install doctl
doctl auth init       # paste API token

# 3. Create the cluster (~5 min)
doctl kubernetes cluster create aceest \
  --region blr1 --size s-1vcpu-2gb --count 2 --1-clicks ingress-nginx

# 4. Save kubeconfig
doctl kubernetes cluster kubeconfig save aceest

# 5. Deploy
kubectl apply -k k8s/base/
kubectl set image deployment/aceest-fitness app=atul411/aceest-fitness:v3.0.0 -n aceest
kubectl rollout status deployment/aceest-fitness -n aceest

# 6. Switch Service to LoadBalancer (gives a public IP)
kubectl patch svc aceest-fitness -n aceest -p '{"spec":{"type":"LoadBalancer"}}'

# 7. Wait ~2 min for the IP to provision
kubectl get svc aceest-fitness -n aceest --watch
# You'll see EXTERNAL-IP populate (e.g. 134.122.45.67)

# 8. Test
curl http://134.122.45.67/programs?format=json
```

**Alternatives** (if you have credits or prefer):
- GKE (Google Cloud, $300 signup credit) — `gcloud container clusters create-auto aceest`
- AKS (Azure, $200 credit) — `az aks create -g rg -n aceest --node-count 2`
- EKS (AWS) — no free tier, but if you have credits: `eksctl create cluster --name aceest`

**Copy this URL into your submission**: `http://<EXTERNAL-IP>/programs`

### Step 3 — Demo the 5 deployment strategies (15 min)

After Step 2, walk through each strategy and capture screenshots:

```bash
# Strategy 1: Rolling Update (default)
kubectl apply -k k8s/rolling-update/
kubectl set image deployment/aceest-fitness app=atul411/aceest-fitness:v2.0.0 -n aceest
kubectl rollout status deployment/aceest-fitness -n aceest
# Screenshot: kubectl get pods -n aceest -w during the rollout

# Strategy 2: Blue/Green
kubectl delete -k k8s/rolling-update/ 2>/dev/null
kubectl apply -k k8s/blue-green/
./scripts/bluegreen-switch.sh green   # flip live traffic
./scripts/bluegreen-switch.sh blue    # rollback
# Screenshot: before+after of `kubectl get endpoints aceest-fitness -n aceest`

# Strategy 3: Canary
kubectl delete -k k8s/blue-green/ 2>/dev/null
kubectl apply -k k8s/canary/
# Screenshot: ingress with canary-weight: "25" annotation
./scripts/canary-promote.sh 50
./scripts/canary-promote.sh 100  # full promotion

# Strategy 4: Shadow (requires Istio)
istioctl install -y
kubectl label namespace aceest istio-injection=enabled --overwrite
kubectl delete -k k8s/canary/ 2>/dev/null
kubectl apply -k k8s/shadow/
# Screenshot: VirtualService showing mirror config

# Strategy 5: A/B Testing
kubectl delete -k k8s/shadow/ 2>/dev/null
kubectl apply -k k8s/ab-testing/
# Test routing:
curl http://<EXTERNAL-IP>/programs                    # → variant A (v2)
curl -H "X-Variant: B" http://<EXTERNAL-IP>/programs  # → variant B (v3)
# Screenshot: the two different responses
```

---

## 4. Generate the submission ZIP (1 min)

If your LMS wants a project ZIP:

```bash
cd "/Users/atul.yadav/Downloads/The code versions for DevOps Assignment"
make submission
# Creates submission/devops-assignment-2.zip with everything except .venv/.git/__pycache__
ls -la submission/
```

The ZIP includes the full project, the SonarQube report, and all docs.

---

## 5. Final pre-submission checklist

Tick these off before clicking "Submit":

### Repo & code
- [ ] GitHub repo is **public** (verify by opening in incognito): https://github.com/atul411/devops-assignment-2
- [ ] At least one GitHub Actions run is **green**: https://github.com/atul411/devops-assignment-2/actions
- [ ] All three tags exist: v1.0.0, v2.0.0, v3.0.0

### Docker
- [ ] Docker Hub repo is public: https://hub.docker.com/r/atul411/aceest-fitness
- [ ] All 4 image tags visible (latest, v1.0.0, v2.0.0, v3.0.0)

### Cluster
- [ ] Cloud K8s cluster running (DigitalOcean / GCP / AWS / Azure)
- [ ] `kubectl get pods -n aceest` shows pods Ready
- [ ] `curl http://<EXTERNAL-IP>/programs` returns the program list
- [ ] All 5 deployment strategies have been demonstrated (screenshots taken)

### Quality
- [ ] SonarQube Quality Gate is shown as **PASSED** (`docs/sonar-report/REPORT.md`)
- [ ] Pytest output shows 48/48 passing
- [ ] Coverage ≥ 80% (currently 80.9%)

### Documents
- [ ] `docs/REPORT.md` (or PDF version) is included in submission
- [ ] All required URLs are in the report (GitHub, Docker Hub, cluster endpoint)
- [ ] Screenshots from § 3 step 3 are saved under `docs/screenshots/`

### Submission upload
- [ ] PDF report uploaded to LMS (or markdown if accepted)
- [ ] Project ZIP uploaded to LMS (if required) — `submission/devops-assignment-2.zip`
- [ ] All URLs pasted into the LMS submission form

---

## 6. Submission text template (paste into LMS submission form)

```
Student: <Your Name>
Course: Introduction to DEVOPS (CSIZG514 / SEZG514) — S1-25
Assignment: 2 — DevOps CI/CD implementation for ACEest Fitness & Gym

Submission artefacts:

1. GitHub repository (public):
   https://github.com/atul411/devops-assignment-2

2. CI/CD pipeline runs (GitHub Actions):
   https://github.com/atul411/devops-assignment-2/actions

3. Docker Hub image registry (all 3 versions):
   https://hub.docker.com/r/atul411/aceest-fitness

4. Live cluster endpoint (Kubernetes):
   http://<EXTERNAL-IP>/programs

5. SonarQube analysis:
   - Quality Gate: PASSED
   - 0 bugs, 0 vulnerabilities, 0 code smells
   - 80.9% test coverage
   - Detailed report at: docs/sonar-report/REPORT.md in the repo

6. Tags / version progression:
   - v1.0.0 — Programs blueprint (read-only)
   - v2.0.0 — + Clients CRUD + progress
   - v3.0.0 — + Auth, workouts, exercises, metrics

7. Key project documents (in repo):
   - docs/REPORT.md       — 3-page assignment report
   - docs/architecture.md  — CI/CD diagram
   - docs/SUBMISSION.md    — submission checklist
   - docs/DEPLOYMENT.md    — operational runbook
   - docs/sonar-report/   — SonarQube quality results

8. Pipeline tooling:
   - Jenkinsfile (declarative, 9 stages, SonarQube quality gate)
   - .github/workflows/ci.yml (secondary CI, Docker Hub auto-push)
   - Dockerfile (multi-stage, python:3.12-slim, non-root, healthcheck)
   - 5 K8s deployment strategies in k8s/{rolling-update,blue-green,canary,shadow,ab-testing}/
```

---

## 7. Post-submission cleanup (after grading)

When you no longer need the cloud cluster (avoids burning your credit):

```bash
doctl kubernetes cluster delete aceest --force

# Local cleanup
docker stop sonarqube jenkins minikube
docker rm sonarqube jenkins
minikube delete
colima stop                # leave it stopped to free RAM
```

---

## Need to look up something specific?

| If you need to know… | Read… |
|---------------------|-------|
| What every requirement maps to | `docs/SUBMISSION.md` |
| The CI/CD architecture / report content | `docs/REPORT.md` |
| How to run any deployment strategy | `docs/DEPLOYMENT.md` |
| What SonarQube found | `docs/sonar-report/REPORT.md` |
| How the app is structured | `README.md` |
