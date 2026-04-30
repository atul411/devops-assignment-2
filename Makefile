.PHONY: help install test lint cov run docker-build docker-run compose-up compose-down clean

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
