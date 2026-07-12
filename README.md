# Network Security — Phishing URL Detection

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white"/>
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/DagsHub-FF6B35?style=for-the-badge&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white"/>
</p>

---

A production-grade **end-to-end Machine Learning system** that classifies URLs as phishing or legitimate. The project covers the full MLOps lifecycle — from raw data ingestion out of MongoDB Atlas, through an automated ML pipeline with statistical drift detection, to a containerized FastAPI service deployed on AWS with CI/CD via GitHub Actions.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [ML Pipeline](#ml-pipeline)
- [Dataset & Features](#dataset--features)
- [Model Performance](#model-performance)
- [API Endpoints](#api-endpoints)
- [CI/CD Pipeline](#cicd-pipeline)
- [AWS EC2 Deployment](#aws-ec2-deployment)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)

---

## Project Overview

Phishing attacks trick users into visiting fake websites that steal credentials, financial data, or personal information. This project builds an ML classifier that analyses **30 URL-based features** (SSL state, domain age, redirect patterns, anchor tags, and more) and predicts whether a URL is **phishing (-1)** or **legitimate (1)**.

Beyond the model itself, the project demonstrates a complete MLOps workflow:

- Modular, production-style Python package (`networksecurity/`)
- Data sourced from **MongoDB Atlas** with automated ingestion
- Statistical data quality checks using the **Kolmogorov–Smirnov test**
- Experiment tracking and metric versioning with **MLflow + DagsHub**
- REST API for on-demand training and batch prediction
- Full **Docker** containerisation with **CI/CD** deployment to AWS ECR + EC2

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Data Storage | MongoDB Atlas |
| ML / Data Science | scikit-learn, pandas, NumPy, SciPy |
| Experiment Tracking | MLflow + DagsHub |
| API Framework | FastAPI + Uvicorn |
| Containerisation | Docker |
| Cloud Storage | AWS S3 |
| Container Registry | AWS ECR |
| Compute | AWS EC2 (self-hosted GitHub Actions runner) |
| CI/CD | GitHub Actions |
| Config & Secrets | python-dotenv |
| Serialisation | dill |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                              │
│                                                                  │
│   phishing.csv  ──►  push_data.py  ──►  MongoDB Atlas           │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                         ML PIPELINE                              │
│                                                                  │
│  Data Ingestion ► Data Validation ► Data Transformation          │
│       │                 │                    │                   │
│  MongoDB → CSV     KS-Test Drift        KNN Imputer +            │
│  Train/Test Split  Detection            StandardScaler           │
│                                                                  │
│                      Model Trainer                               │
│                  ┌──────────────────┐                            │
│                  │ Random Forest    │                            │
│                  │ Decision Tree    │  GridSearchCV              │
│                  │ Gradient Boost   │ ──────────► Best Model     │
│                  │ Logistic Reg     │                            │
│                  │ AdaBoost         │                            │
│                  └──────────────────┘                            │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
             MLflow + DagsHub          AWS S3
             (metric tracking)     (artifact storage)
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                        SERVING LAYER                             │
│                                                                  │
│   FastAPI  ──►  GET /train    (trigger full pipeline)            │
│            ──►  POST /predict (upload CSV → predictions table)   │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       CI/CD PIPELINE                             │
│                                                                  │
│  GitHub Push ► GitHub Actions ► Docker Build ► Push to ECR      │
│                                              ► Deploy on EC2     │
└──────────────────────────────────────────────────────────────────┘
```

---

## ML Pipeline

The pipeline is implemented as four sequential, independently testable components. Each component produces a typed **artifact dataclass** that is passed as input to the next stage — making the pipeline easy to debug, resume, and extend.

### 1. Data Ingestion

- Connects to **MongoDB Atlas** over a secure SRV connection (TLS via `certifi`)
- Exports the `network_data` collection from the `phishing` database into a pandas DataFrame
- Saves the raw dataset to a timestamped feature store directory as `phishing.csv`
- Splits into **train (80%) / test (20%)** and saves both to the `ingested/` directory
- Returns a `DataIngestionArtifact` with the train and test file paths

### 2. Data Validation

- Validates that the DataFrame column count matches the `schema.yaml` definition (31 columns including target)
- Runs a **Kolmogorov–Smirnov two-sample test** on every feature column to detect distribution drift between train and test sets
- Drift threshold: `p-value < 0.05` → drift detected
- Writes a per-column drift report to `drift_report/report.yaml`
- Routes valid data to `validated/` and flags invalid data to `invalid/`
- Returns a `DataValidationArtifact` with validation status and file paths

### 3. Data Transformation

- Applies a **KNN Imputer** (`n_neighbors=3, weights="uniform"`) to handle missing values in all numerical columns
- Wraps the imputer in a scikit-learn `Pipeline` object
- Fits the preprocessor on training data and applies it to both train and test sets
- Saves the fitted preprocessor as `preprocessing.pkl` to both `artifacts/` and `final_model/`
- Outputs transformed data as NumPy `.npy` arrays for fast, compact storage
- Returns a `DataTransformationArtifact` with paths to arrays and the preprocessing object

### 4. Model Trainer

Trains five classifiers with **GridSearchCV** hyperparameter tuning and selects the best:

| Model | Hyperparameters Tuned |
|---|---|
| Random Forest | `n_estimators`: [8, 16, 32, 64, 128, 256] |
| Decision Tree | `criterion`: [gini, entropy] |
| Gradient Boosting | `learning_rate`, `subsample`, `n_estimators` |
| Logistic Regression | default |
| AdaBoost | `learning_rate`, `n_estimators` |

Post-selection checks:
- **Overfitting guard**: rejects any model where the train/test F1 gap exceeds 5%
- **Minimum score**: rejects models below 60% F1 on the test set

Logging and storage:
- Logs **F1, Precision, Recall** for both train and test to **MLflow** (remote tracking server on DagsHub)
- Saves the best model wrapped in a `NetworkModel` (preprocessor + model) to `final_model/model.pkl`
- Syncs both `Artifacts/` and `final_model/` to **AWS S3** after training

---

## Dataset & Features

The dataset contains **30 input features** extracted from URL structure, page content, and external signals. Each feature is encoded as:
- `-1` → phishing indicator
- `0`  → suspicious / neutral
- `1`  → legitimate indicator

| Category | Features |
|---|---|
| URL Structure | `having_IP_Address`, `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix` |
| Domain & SSL | `having_Sub_Domain`, `SSLfinal_State`, `Domain_registeration_length`, `age_of_domain`, `DNSRecord`, `HTTPS_token` |
| Page Content | `Favicon`, `Request_URL`, `URL_of_Anchor`, `Links_in_tags`, `SFH`, `Submitting_to_email` |
| JavaScript Behaviour | `Abnormal_URL`, `Redirect`, `on_mouseover`, `RightClick`, `popUpWidnow`, `Iframe` |
| External Signals | `web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`, `Statistical_report`, `port` |
| **Target** | `Result` → `-1` phishing / `1` legitimate |

---

## Model Performance

The best model (Random Forest, tuned via GridSearchCV) achieved the following on the held-out test set:

| Metric | Train | Test |
|---|---|---|
| F1 Score | ~0.99 | **~0.977** |
| Precision | ~0.99 | ~0.977 |
| Recall | ~0.99 | ~0.977 |

All training runs are logged and versioned in DagsHub. You can browse the experiment history at:
`https://dagshub.com/pratikjivanjadhav77/network-security`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check — returns welcome message |
| `GET` | `/train` | Triggers the full training pipeline end-to-end |
| `POST` | `/predict` | Upload a CSV (30 feature columns) → returns predictions as an HTML table |

### Running locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Trigger training

```bash
curl http://localhost:8000/train
```

### Predict from a CSV file

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@test_data/test.csv"
```

The response is a Bootstrap-styled HTML table with a `predicted_column` appended to each row. The output is also saved to `prediction_output/output.csv`.

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/main.yaml`) runs automatically on every push to `main`:

```
Push to main
     │
     ▼
┌───────────────────────┐
│   1. Integration      │  ubuntu-latest
│   Lint + unit tests   │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│   2. Build & Push     │  ubuntu-latest
│   docker build        │
│   Push image → ECR    │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│   3. Deploy to EC2    │  self-hosted runner
│   Pull image from ECR │
│   docker run :8080    │
│   docker system prune │
└───────────────────────┘
```

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_REGION` | e.g. `us-east-1` |
| `ECR_REPOSITORY_NAME` | ECR repository name |
| `AWS_ECR_LOGIN_URI` | ECR registry URI (account.dkr.ecr.region.amazonaws.com) |
| `MONGO_DB_URL` | MongoDB Atlas connection string |

---

## AWS EC2 Deployment

The application is deployed on an **AWS EC2** instance acting as both the production server and the self-hosted GitHub Actions runner. This means every push to `main` automatically replaces the running container with the latest image — zero manual steps.

### How it works

```
GitHub Actions (Job 3: continuous-deployment)
          │
          │  runs-on: self-hosted
          │  (the EC2 instance registers itself as a runner)
          │
          ▼
┌──────────────────────────────────────────────┐
│               AWS EC2 Instance               │
│                                              │
│  1. aws ecr get-login-token                  │
│     → authenticates Docker with ECR          │
│                                              │
│  2. docker pull <ecr-uri>/<repo>:latest      │
│     → downloads the freshly built image      │
│                                              │
│  3. docker run -d \                          │
│       -p 8080:8000 \                         │
│       --name=network-security \              │
│       -e AWS_ACCESS_KEY_ID=... \             │
│       -e AWS_SECRET_ACCESS_KEY=... \         │
│       -e AWS_REGION=... \                    │
│       <ecr-uri>/<repo>:latest                │
│                                              │
│  4. docker system prune -f                   │
│     → removes dangling images to free disk   │
│                                              │
│  FastAPI serves on  →  port 8080             │
└──────────────────────────────────────────────┘
```

### EC2 Setup (self-hosted runner)

To register the EC2 instance as a GitHub Actions runner:

**1. Launch an EC2 instance**
- AMI: Ubuntu 22.04 LTS
- Instance type: `t2.medium` or higher (training is CPU-intensive)
- Security group: open inbound port `8080` (application) and `22` (SSH)
- Attach an IAM role with `AmazonEC2ContainerRegistryReadOnly` and `AmazonS3FullAccess` policies

**2. Install Docker on the instance**

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

**3. Install AWS CLI**

```bash
sudo apt-get install -y awscli
aws configure   # enter your AWS credentials
```

**4. Register the self-hosted runner**

Go to your GitHub repository → **Settings → Actions → Runners → New self-hosted runner**, then follow the generated commands on the EC2 instance. Once registered, the instance appears as `self-hosted` in your workflow.

**5. Start the runner**

```bash
./run.sh   # or install as a service: sudo ./svc.sh install && sudo ./svc.sh start
```

### Port mapping

| Host (EC2) | Container | Service |
|---|---|---|
| `8080` | `8000` | FastAPI + Uvicorn |

The application is accessible at `http://<ec2-public-ip>:8080` after each successful deployment.

### AWS services used

| Service | Purpose |
|---|---|
| **EC2** | Hosts the Docker container and runs the GitHub Actions self-hosted runner |
| **ECR** | Private Docker image registry — stores the built image per push |
| **S3** | Stores pipeline artifacts (`Artifacts/`) and the final trained model (`final_model/`) |
| **IAM** | Scoped permissions for GitHub Actions (ECR push) and EC2 (ECR pull + S3 read/write) |

---

## Project Structure

```
networksecurity/
│
├── networksecurity/                    # Core Python package
│   ├── components/
│   │   ├── data_ingestion.py           # MongoDB → feature store → train/test split
│   │   ├── data_validation.py          # Schema check + KS drift detection
│   │   ├── data_transformation.py      # KNN imputer + preprocessing pipeline
│   │   └── model_trainer.py            # GridSearchCV + MLflow tracking
│   │
│   ├── entity/
│   │   ├── config_entity.py            # Pipeline config dataclasses
│   │   └── artifact_entity.py          # Pipeline artifact dataclasses
│   │
│   ├── pipeline/
│   │   └── training_pipeline.py        # Orchestrates all four components + S3 sync
│   │
│   ├── cloud/
│   │   └── s3_syncer.py                # AWS S3 upload/download helpers
│   │
│   ├── constant/
│   │   └── training_pipeline/          # All pipeline constants (paths, names, ratios)
│   │
│   ├── utils/
│   │   ├── main_utils/utils.py         # YAML IO, pickle save/load, model evaluation
│   │   └── ml_utils/
│   │       ├── metric/                 # Classification metric helpers
│   │       └── model/estimator.py      # NetworkModel wrapper (preprocessor + model)
│   │
│   ├── exception/exception.py          # Custom exception with full traceback
│   └── logging/logger.py              # Timestamped rotating file logger
│
├── templates/table.html                # Jinja2 prediction results template
├── data_schema/schema.yaml             # Column and type schema for validation
├── test_data/test.csv                  # Sample 5-row prediction input
│
├── app.py                              # FastAPI application entry point
├── push_data.py                        # One-time CSV → MongoDB loader
├── setup.py                            # Editable package installer
├── requirements.txt                    # All Python dependencies
├── Dockerfile                          # Container build definition
└── .github/workflows/main.yaml         # CI/CD pipeline (3 jobs)
```

---

## Getting Started

### Prerequisites

- Python 3.10
- MongoDB Atlas cluster
- AWS account with S3, ECR, and EC2 access
- DagsHub account (for MLflow remote tracking)

### 1. Clone the repository

```bash
git clone https://github.com/pratikjivanjadhav77/network-security.git
cd network-security
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
MONGO_DB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### 5. Load data into MongoDB

```bash
python push_data.py
```

### 6. Start the API server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Trigger training

Open your browser and visit `http://localhost:8000/train`, or:

```bash
curl http://localhost:8000/train
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MONGO_DB_URL` | Yes | MongoDB Atlas SRV connection string |
| `AWS_ACCESS_KEY_ID` | For S3/ECR | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | For S3/ECR | AWS IAM secret key |
| `AWS_DEFAULT_REGION` | For S3/ECR | AWS region (e.g. `us-east-1`) |

---

<p align="center">
  Built end-to-end with &nbsp;
  <b>scikit-learn · FastAPI · MongoDB Atlas · MLflow · DagsHub · Docker · AWS S3 · AWS ECR · GitHub Actions</b>
</p>
