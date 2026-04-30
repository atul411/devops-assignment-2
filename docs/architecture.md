# CI/CD Architecture

```
+----------------+       +-------------------+        +--------------------+
| Developer      | push  | GitHub            |  poll  | Jenkins (controller)|
| (git tag vN.N) +------>| atul411/          +<------>| pipeline.script     |
+----------------+       | devops-assignment-2|(1 min)+----------+---------+
                         +-------------------+                   |
                                                                 v
                                       +-------------------------+--------------------+
                                       |                          PIPELINE                              |
                                       +--------------------------------------------------------------+
                                       | 1. Checkout                                                  |
                                       | 2. python -m venv .venv && pip install -r requirements*.txt |
                                       | 3. flake8 app tests                                          |
                                       | 4. pytest --cov=app --cov-report=xml                         |
                                       | 5. sonar-scanner   ---->  SonarQube Server                   |
                                       | 6. waitForQualityGate (timeout 5m, abort on fail)            |
                                       | 7. docker build -t $USER/aceest-fitness:$BUILD               |
                                       | 8. docker push (Docker Hub)                                  |
                                       | 9. kubectl apply -k k8s/<strategy>                           |
                                       |10. kubectl rollout status (auto-rollback on failure)         |
                                       +--------------------------------------------------------------+
                                                                 |
                                                                 v
                                                  +--------------+--------------+
                                                  |        Kubernetes           |
                                                  |  (Minikube / EKS / GKE)     |
                                                  |                             |
                                                  |  Namespace: aceest          |
                                                  |  +---- Deployments ----+    |
                                                  |  | rolling / blue-green |    |
                                                  |  | canary / shadow / ab |    |
                                                  |  +----------------------+    |
                                                  |  Service / Ingress / PVC    |
                                                  +-----------------------------+
                                                                 |
                                                                 v
                                                       https://aceest.local
                                                       (end users + monitoring)
```

## Component responsibilities

| Stage | Tool | Outputs |
|-------|------|---------|
| Source control | Git + GitHub | Commits, tags `v1.0.0` / `v2.0.0` / `v3.0.0` |
| Build trigger | Jenkins SCM polling | New build per commit on `main` |
| Static analysis | flake8, SonarQube | Lint failures, code-smell + security report |
| Quality gate | SonarQube | Blocks pipeline on coverage/critical issues |
| Test | pytest + pytest-cov | JUnit XML, coverage XML |
| Image build | Docker (multi-stage) | `:${BUILD_NUMBER}` and `:latest` tags |
| Image registry | Docker Hub | Versioned images for K8s |
| Deploy | kubectl + Kustomize | Rolled out to chosen strategy folder |
| Runtime | Kubernetes (nginx-ingress / Istio) | Routed traffic with chosen strategy |
| Rollback | kubectl rollout undo / Service-selector flip | Instant revert |

## Strategy decision matrix

| Strategy | Rollback time | Traffic risk | Infra cost | Best for |
|----------|---------------|--------------|------------|----------|
| Rolling update | minutes | progressive | base | default for safe schema-compatible changes |
| Blue/Green | seconds (selector flip) | none until flip | 2× pods during cutover | risky changes needing instant rollback |
| Canary | minutes (drain canary) | bounded by % | 1.x× | quantitative validation under prod traffic |
| Shadow | n/a (no user impact) | zero | 2× compute | side-effect-free perf / behaviour testing |
| A/B testing | per-cohort flip | per-cohort | 2× | feature evaluation by user segment |
