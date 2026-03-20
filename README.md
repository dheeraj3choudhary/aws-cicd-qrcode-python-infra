# aws-cicd-qrcode-python-app

![App Pipeline](https://img.shields.io/badge/pipeline-app-blue?style=flat-square&logo=amazonaws)
![Python](https://img.shields.io/badge/python-3.12-yellow?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/flask-3.1-lightgrey?style=flat-square&logo=flask)
![Docker](https://img.shields.io/badge/docker-multi--stage-2496ED?style=flat-square&logo=docker)
![Deploy](https://img.shields.io/badge/deploy-CodeDeploy-orange?style=flat-square&logo=amazonaws)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)

Python QR Code Generator application — Flask API + dark themed frontend, Dockerised and deployed to EC2 via AWS CodeDeploy.

---

## Repository Structure

```
aws-cicd-qrcode-python-app/
├── app.py                        # Flask app — /, /health, /generate endpoints
├── requirements.txt              # Pinned dependencies
├── Dockerfile                    # Multi-stage build (builder + runtime, non-root)
├── buildspec-test.yml            # CodeBuild stage 1 — install + pytest
├── buildspec-docker.yml          # CodeBuild stage 2 — docker build + ECR push
├── appspec.yml                   # CodeDeploy lifecycle hook mapping
├── public/
│   └── index.html                # Dark themed frontend UI
├── tests/
│   └── test_app.py               # 16 pytest unit tests
├── scripts/
│   ├── before_install.sh         # Stop + remove existing container
│   ├── after_install.sh          # IMDSv2 region lookup, ECR login, docker pull
│   ├── application_start.sh      # docker run with restart policy
│   └── validate_service.sh       # /health curl with 10 retries
├── .gitignore
└── README.md
```

---

## App Pipeline

```
CodeCommit push to main
        │
        ▼
┌───────────────┐
│    Source     │  Pulls from aws-cicd-qrcode-python-app @ main
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Build & Test  │  buildspec-test.yml
│               │  - pip install -r requirements.txt
│               │  - PYTHONPATH=. pytest tests/ --cov --junitxml
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Docker & Push │  buildspec-docker.yml
│               │  - Read ECR URI from SSM /qrcode/ecr/repo-uri
│               │  - docker build (ECR Public base image)
│               │  - docker push :latest to ECR
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    Deploy     │  CodeDeploy — appspec.yml
│               │  BeforeInstall  → before_install.sh
│               │  AfterInstall   → after_install.sh
│               │  ApplicationStart → application_start.sh
│               │  ValidateService  → validate_service.sh
└───────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the frontend UI |
| `GET` | `/health` | Health check — returns `{"status":"healthy"}` |
| `POST` | `/generate` | Generate a QR code — returns PNG binary |

### POST /generate

**Request body (JSON):**

```json
{
  "data": "https://example.com",
  "size": 10,
  "border": 4
}
```

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `data` | string | yes | — | Non-empty |
| `size` | integer | no | `10` | 1–50 |
| `border` | integer | no | `4` | 0–20 |

**Response:** `image/png` binary

**Example:**

```bash
curl -X POST http://<EC2_IP>:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"data": "https://example.com"}' \
  --output qrcode.png
```

---

## Running Locally

```bash
# Clone
git clone https://git-codecommit.<region>.amazonaws.com/v1/repos/aws-cicd-qrcode-python-app
cd aws-cicd-qrcode-python-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

App will be available at `http://localhost:5000`.

---

## Running with Docker Locally

```bash
# Build
docker build -t qrcode-app .

# Run
docker run -p 5000:5000 qrcode-app
```

App will be available at `http://localhost:5000`.

---

## Running Tests

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v --cov=app --cov-report=term-missing
```

**Test coverage:**

| Area | Tests |
|------|-------|
| Health check | 2 |
| Index page | 2 |
| Generate — happy path | 4 |
| Generate — validation errors | 6 |
| Error handlers | 2 |
| **Total** | **16** |

---

## Docker Image

- **Base image:** `public.ecr.aws/docker/library/python:3.12-slim` (ECR Public — no rate limits)
- **Multi-stage build:** `builder` installs deps into `/venv`, `runtime` copies only venv + source
- **Non-root user:** runs as `appuser` (UID 1001)
- **Health check:** built-in Docker `HEALTHCHECK` hitting `/health` every 30s
- **Port:** `5000`

---

## CodeDeploy Lifecycle

| Hook | Script | What it does |
|------|--------|-------------|
| `BeforeInstall` | `before_install.sh` | Stops and removes the existing container |
| `AfterInstall` | `after_install.sh` | IMDSv2 region lookup, ECR login, `docker pull :latest` |
| `ApplicationStart` | `application_start.sh` | `docker run` with `--restart unless-stopped` |
| `ValidateService` | `validate_service.sh` | 10 × 5s retries curling `/health`, dumps logs on failure |

---

## Accessing the App

After a successful deployment the app URL is available in:

**CloudFormation Console → `qrcode-compute` stack → Outputs → `AppUrl`**

```
http://<ElasticIP>:5000
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `5000` | Port the Flask app listens on |
| `APP_HOST` | `0.0.0.0` | Host the Flask app binds to |

---

## Related Repository

| Repo | Description |
|------|-------------|
| [`aws-cicd-qrcode-python-infra`](https://git-codecommit.<region>.amazonaws.com/v1/repos/aws-cicd-qrcode-python-infra) | CloudFormation stacks, infra pipeline, teardown script |