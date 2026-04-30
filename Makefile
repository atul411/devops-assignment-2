.PHONY: help install test lint cov run docker-build docker-run compose-up compose-down clean pdf html submission

help:
	@echo "ACEest Fitness — common dev tasks"
	@echo "  make install        Install dev dependencies into .venv"
	@echo "  make test           Run pytest"
	@echo "  make cov            Run pytest with coverage report"
	@echo "  make lint           Run flake8"
	@echo "  make run            Run Flask dev server (FEATURE_LEVEL=3)"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run image on :5000"
	@echo "  make compose-up     docker-compose up -d"
	@echo "  make compose-down   docker-compose down -v"
	@echo "  make clean          Remove build/test artifacts"
	@echo ""
	@echo "Submission packaging:"
	@echo "  make pdf            Convert REPORT.md and SUBMIT.md to PDF (needs pandoc + basictex)"
	@echo "  make html           Convert REPORT.md and SUBMIT.md to standalone HTML"
	@echo "  make submission     Build submission/devops-assignment-2.zip ready for LMS upload"

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements-dev.txt

test:
	.venv/bin/pytest -v

cov:
	.venv/bin/pytest --cov=app --cov-report=term-missing --cov-report=xml

lint:
	.venv/bin/flake8 app tests --max-line-length=120 --extend-ignore=E501,W503

run:
	FEATURE_LEVEL=3 DATABASE=./aceest_dev.db .venv/bin/python -m flask --app app:create_app run --debug --host 0.0.0.0 --port 5000

docker-build:
	docker build -t aceest-fitness:dev .

docker-run:
	docker run --rm -p 5000:5000 -e FEATURE_LEVEL=3 -v aceest-data:/data aceest-fitness:dev

compose-up:
	docker-compose up -d --build

compose-down:
	docker-compose down -v

clean:
	rm -rf .pytest_cache .coverage coverage.xml htmlcov test-results.xml aceest_dev.db __pycache__ app/__pycache__ tests/__pycache__

pdf: html submission/REPORT.pdf submission/SUBMIT.pdf submission/sonar-REPORT.pdf

CHROME ?= /Applications/Google Chrome.app/Contents/MacOS/Google Chrome

submission/%.pdf: submission/%.html
	@if [ -x "$(CHROME)" ]; then \
	  echo "Generating $@ via Chrome headless..."; \
	  "$(CHROME)" --headless --disable-gpu --no-pdf-header-footer \
	    --print-to-pdf="$@" "file://$(PWD)/$<" 2>/dev/null; \
	elif command -v pandoc >/dev/null && command -v pdflatex >/dev/null; then \
	  echo "Generating $@ via pandoc+pdflatex..."; \
	  pandoc $< -o $@ --pdf-engine=pdflatex --variable geometry:margin=1in; \
	else \
	  echo "PDF generation needs Chrome or pandoc+basictex. HTML available at $<"; \
	  exit 1; \
	fi

submission:
	mkdir -p submission
	@echo "Bundling project (excluding .venv, .git internals, caches, db files) ..."
	cd .. && zip -r "The code versions for DevOps Assignment/submission/devops-assignment-2.zip" \
	  "The code versions for DevOps Assignment" \
	  -x "*/.venv/*" "*/__pycache__/*" "*/.pytest_cache/*" "*/.git/objects/pack/*" \
	     "*/htmlcov/*" "*/.coverage" "*/coverage.xml" "*/test-results.xml" \
	     "*/.DS_Store" "*/aceest_dev.db" "*/submission/*" >/dev/null
	@ls -la submission/devops-assignment-2.zip
	@echo "Wrote submission/devops-assignment-2.zip"

html: submission/REPORT.html submission/SUBMIT.html submission/sonar-REPORT.html

submission/REPORT.html: docs/REPORT.md
	@mkdir -p submission
	@which pandoc >/dev/null || (echo "pandoc not found. Install with: brew install pandoc" && exit 1)
	pandoc docs/REPORT.md -o submission/REPORT.html --standalone --metadata title="ACEest Fitness — DevOps CI/CD Assignment Report" --css=https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css

submission/SUBMIT.html: docs/SUBMIT.md
	@mkdir -p submission
	@which pandoc >/dev/null || exit 1
	pandoc docs/SUBMIT.md -o submission/SUBMIT.html --standalone --metadata title="Submission Guide" --css=https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css

submission/sonar-REPORT.html: docs/sonar-report/REPORT.md
	@mkdir -p submission
	@which pandoc >/dev/null || exit 1
	pandoc docs/sonar-report/REPORT.md -o submission/sonar-REPORT.html --standalone --metadata title="SonarQube Analysis" --css=https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css
