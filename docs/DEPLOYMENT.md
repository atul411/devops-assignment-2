# Deployment playbook

This file walks through what's left to make the cluster fully live and reachable. It assumes you have the GitHub repo at `https://github.com/atul411/devops-assignment-2`.

## Status (verified locally on this Mac)

- ✅ Local pytest suite: 48/48 passing, 81% coverage
- ✅ flake8: clean
- ✅ Local Minikube cluster: up (control plane Running, ingress addon enabled)
- ✅ K8s manifests: all 6 strategy folders apply cleanly via `kubectl apply -k k8s/<strategy>/`
- ✅ GitHub Actions CI run: passed (test job 36s, docker build job 13s)
- ⚠️ Pods on Minikube: `ImagePullBackOff` — image `atul411/aceest-fitness:latest` is not on Docker Hub yet (needs your account)
- ⚠️ Local Docker build: blocked by Zscaler TLS interception inside the python:3.12-slim build container (corp-network specific). Build succeeds in clean networks (proven by GH Actions).

## Remaining steps you need to do

### 1. Create a Docker Hub account and access token (5 min)

1. Sign up at https://hub.docker.com using username **`atul411`** (or update placeholders if different).
2. Settings → Personal access tokens → New Access Token → name `gh-actions-push`, permission **Read, Write, Delete**.
3. Copy the token (shown only once).

### 2. Add the token to GitHub repo secrets (1 min)

```bash
cd "/Users/atul.yadav/Downloads/The code versions for DevOps Assignment"
gh secret set DOCKERHUB_TOKEN -a actions
# paste token when prompted
```

After that, every push to `main` will automatically build AND push the image to Docker Hub. Tag pushes (`v1.0.0`, `v2.0.0`, `v3.0.0`) will create versioned image tags too.

### 3. Trigger a build (push an empty commit or push tags)

```bash
# Re-trigger so the new workflow runs with the secret
git commit --allow-empty -m "Trigger CI with DOCKERHUB_TOKEN secret"
git push
gh run watch
```

Confirm the image landed: https://hub.docker.com/r/atul411/aceest-fitness/tags

### 4. Choose a target cluster

#### A) Local Minikube (development demo)

```bash
# Already started; if not:
minikube start --driver=docker --cpus=2 --memory=4g
minikube addons enable ingress

# Apply
kubectl apply -k k8s/base/
kubectl apply -k k8s/rolling-update/        # OR another strategy

# Add hostname to /etc/hosts (Minikube IP)
echo "$(minikube ip) aceest.local" | sudo tee -a /etc/hosts

# Open port forwarding (Minikube on Apple Silicon needs the tunnel)
minikube tunnel    # leave running in another terminal
# OR
kubectl -n aceest port-forward svc/aceest-fitness 8080:80
# then http://localhost:8080
```

#### B) Free-tier cloud K8s (so the grader can hit the URL)

| Provider | Free tier? | Notes |
|----------|-----------|-------|
| **DigitalOcean Kubernetes** | $200 free credit on signup; no permanent free tier | Easiest UI; loads of one-click guides |
| **GKE Autopilot** | $300 GCP signup credit; small clusters cheap | Best K8s integration |
| **AWS EKS** | No free tier (control plane $0.10/hr) | More complex setup |
| **Azure AKS** | $200 Azure credit; control plane free | Decent for short-lived demos |
| **Civo K8s** | $250 free credit; cheapest after | Fast spin-up; less common |

For a quick public endpoint that grader can curl:

```bash
# Example with DigitalOcean (after `doctl auth init`):
doctl kubernetes cluster create aceest --region blr1 --size s-1vcpu-2gb --count 1
doctl kubernetes cluster kubeconfig save aceest

kubectl apply -k k8s/base/
kubectl apply -k k8s/rolling-update/

# LoadBalancer Service patches the base Service from ClusterIP -> LoadBalancer
kubectl patch svc aceest-fitness -n aceest -p '{"spec":{"type":"LoadBalancer"}}'
kubectl get svc aceest-fitness -n aceest --watch    # wait for EXTERNAL-IP

# Submit that EXTERNAL-IP as your cluster endpoint URL.
```

### 5. Demonstrate each deployment strategy

```bash
# Rolling update (default)
kubectl apply -k k8s/base/
kubectl apply -k k8s/rolling-update/
# Then update the image tag and watch:
kubectl set image deployment/aceest-fitness app=atul411/aceest-fitness:v3.0.0 -n aceest
kubectl rollout status deployment/aceest-fitness -n aceest

# Blue/Green
kubectl delete -k k8s/rolling-update/ 2>/dev/null
kubectl apply -k k8s/blue-green/
./scripts/bluegreen-switch.sh green     # flip traffic
./scripts/bluegreen-switch.sh blue      # roll back

# Canary
kubectl delete -k k8s/blue-green/ 2>/dev/null
kubectl apply -k k8s/canary/
./scripts/canary-promote.sh 50          # ramp to 50%
./scripts/canary-promote.sh 100         # full promotion

# Shadow (REQUIRES Istio)
istioctl install -y
kubectl label namespace aceest istio-injection=enabled --overwrite
kubectl delete -k k8s/canary/ 2>/dev/null
kubectl apply -k k8s/shadow/

# A/B testing
kubectl delete -k k8s/shadow/ 2>/dev/null
kubectl apply -k k8s/ab-testing/
curl -H "X-Variant: B" http://aceest.local/health    # routes to variant B
curl http://aceest.local/health                      # routes to variant A
```

### 6. Set up Jenkins (assignment requirement)

The Jenkinsfile is fully written. To run a Jenkins server locally:

```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# Get initial admin password:
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Open http://localhost:8080, install suggested plugins, create admin user.
# Install plugins: Pipeline, Docker Pipeline, SonarQube Scanner, Kubernetes CLI.
# Manage Jenkins → Credentials → add:
#   - dockerhub-credentials (Username with password) — your Docker Hub token
#   - kubeconfig (Secret file) — content of ~/.kube/config
# Manage Jenkins → System → SonarQube servers → name "SonarQube"
# New Item → Pipeline → SCM = Git → URL https://github.com/atul411/devops-assignment-2 → Jenkinsfile path
```

### 7. Set up SonarQube (assignment requirement)

```bash
docker run -d --name sonarqube \
  -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
  sonarqube:community

# Open http://localhost:9000 (admin/admin, change password on first login).
# Create a project key "aceest-fitness" matching sonar-project.properties.
# In Jenkins → Manage Jenkins → System → SonarQube servers, set the URL + auth token.
# Trigger a Jenkins build; the Quality Gate stage will block on coverage/issues.
```

## What the grader will see

After completing the steps above:

| Artifact | Where |
|----------|-------|
| GitHub repo (public) | https://github.com/atul411/devops-assignment-2 |
| GitHub Actions runs | https://github.com/atul411/devops-assignment-2/actions |
| Docker Hub repo | https://hub.docker.com/r/atul411/aceest-fitness/tags |
| Cluster endpoint | The `EXTERNAL-IP` from `kubectl get svc aceest-fitness -n aceest` after switching to LoadBalancer |
| Jenkins URL | Whatever you expose (or screenshots of the pipeline runs) |
| SonarQube URL | Whatever you expose (or screenshots of the dashboard) |
