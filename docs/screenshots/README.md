# Screenshots — what to capture for submission

Some screenshots have been captured automatically. Others need you (because they require an authenticated browser session that headless Chrome can't reproduce). All URLs use credentials I configured for you.

## ✅ Already captured (auto)

| File | What it shows |
|------|---------------|
| `github-repo.png` | The public GitHub repo home page (https://github.com/atul411/devops-assignment-2) |
| `github-actions.png` | GitHub Actions runs, all green |
| `jenkins-build-7-stages.json` | Jenkins pipeline stages (SUCCESS, 44s) — proof in JSON |
| `jenkins-build-7-summary.json` | Jenkins build #7 metadata |
| `jenkins-build-7-console.txt` | Full console log of the green build |
| `jenkins-job-info.json` | Jenkins job configuration metadata |

## 📷 You need to capture these (5 minutes total)

Open each URL → take a screenshot → save under `docs/screenshots/`.

| # | What | URL | Login | Suggested filename |
|---|------|-----|-------|--------------------|
| 1 | Jenkins build #7 page (green pipeline graph) | http://localhost:8080/job/aceest-fitness/7/ | `admin` / `AdminPass123!` | `jenkins-build-7.png` |
| 2 | Jenkins job page (showing all 7 builds) | http://localhost:8080/job/aceest-fitness/ | same | `jenkins-job.png` |
| 3 | Jenkins build #7 console output | http://localhost:8080/job/aceest-fitness/7/console | same | `jenkins-console.png` |
| 4 | SonarQube project dashboard (Quality Gate PASSED) | http://localhost:9000/dashboard?id=aceest-fitness | `admin` / `AdminPass123!` | `sonarqube-dashboard.png` |
| 5 | SonarQube measures (coverage, complexity, etc.) | http://localhost:9000/component_measures?id=aceest-fitness | same | `sonarqube-measures.png` |
| 6 | SonarQube issues (0 open) | http://localhost:9000/project/issues?id=aceest-fitness&resolved=false | same | `sonarqube-issues.png` |

## 📷 After Docker Hub setup (additional)

Once you set the `DOCKERHUB_TOKEN` secret and a CI run pushes the image:

| # | What | URL | Filename |
|---|------|-----|----------|
| 7 | Docker Hub repo with all tags | https://hub.docker.com/r/atul411/aceest-fitness/tags | `dockerhub-tags.png` |

## 📷 After K8s deployment (additional, if you do cloud K8s)

Once an image is on Docker Hub and you've deployed to a cluster:

| # | What | Command/URL | Filename |
|---|------|-------------|----------|
| 8 | Pods Running | `kubectl get all -n aceest` (terminal screenshot) | `kubectl-get-all.png` |
| 9 | App responding | `curl http://<EXTERNAL-IP>/programs?format=json` | `curl-app.png` |
| 10 | Each strategy demo (5 separate) | Per `docs/SUBMIT.md` § 3 step 3 | `strategy-rolling.png`, `strategy-blue-green.png`, etc. |

## How to take a screenshot on macOS

- **Full screen**: ⌘ + ⇧ + 3 → saves to Desktop
- **Selected window**: ⌘ + ⇧ + 4 → press Space → click window
- **Selected area**: ⌘ + ⇧ + 4 → drag

Then drag the file from Desktop into `docs/screenshots/` (or use Finder to move).

## Bundle into submission

After all screenshots are saved:

```bash
make submission   # rebuilds devops-assignment-2.zip including the screenshots
```
