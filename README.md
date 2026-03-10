# 🚕 NYC Taxi Data Pipeline

An end-to-end batch ELT data pipeline processing **90M+ NYC taxi trips** using modern Data Engineering tools. Built as a portfolio project demonstrating real-world DE best practices.

---

## 📐 Architecture

```
NYC TLC (Public S3)
       │
       ▼
  Python Ingest          ← Schema enforcement with pandas
  (scripts/ingest.py)    ← Idempotent uploads (skip if exists)
       │
       ▼
Google Cloud Storage     ← Data Lake (Raw Zone)
  raw/yellow/2019/       ← Immutable parquet files
  raw/green/2019/
       │
       ▼
  BigQuery External      ← Reference layer (no copy cost)
  Tables
       │
       ▼
  BigQuery Native        ← Partitioned by date
  Tables                 ← Clustered by location IDs
  (nyc_taxi_raw)         ← 53% query cost reduction
       │
       ▼
  dbt Transformations
  ┌─────────────────┐
  │ Staging (views) │  ← Type casting, cleaning, filtering
  │ Core (tables)   │  ← Dimensions + Incremental Fact table
  │ Marts (tables)  │  ← Business analytics aggregations
  └─────────────────┘
       │
       ▼
Apache Airflow DAG       ← Orchestration & scheduling
  (monthly schedule)     ← Catchup & backfill support
```

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11 | Ingestion scripts |
| uv | latest | Fast Python package manager |
| Apache Airflow | 2.9.3 | Pipeline orchestration |
| dbt Core | 1.8.0 | Data transformation |
| dbt-bigquery | 1.8.0 | dbt BigQuery adapter |
| Google BigQuery | — | Cloud data warehouse |
| Google Cloud Storage | — | Data lake |
| Docker + Compose | 29.x | Containerization |
| PostgreSQL | 15 | Airflow metadata database |

---

## 📊 Dataset

- **Source:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Coverage:** Yellow + Green taxi trips, full year 2019
- **Volume:** ~90M rows, ~900MB raw parquet
- **Yellow taxi:** 84,598,444 trips
- **Green taxi:** 6,300,985 trips

---

## 🗂️ Project Structure

```
nyc-taxi-pipeline/
├── dags/
│   └── nyc_taxi_pipeline.py    # Airflow DAG
├── scripts/
│   ├── ingest.py               # Download TLC → GCS
│   ├── load_to_bq.py           # GCS → BigQuery loader
│   └── __init__.py
├── nyc_taxi/                   # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   ├── stg_yellow_tripdata.sql
│   │   │   └── stg_green_tripdata.sql
│   │   ├── core/
│   │   │   ├── dim_zones.sql
│   │   │   └── fct_trips.sql
│   │   └── marts/
│   │       ├── mart_daily_revenue.sql
│   │       ├── mart_hourly_patterns.sql
│   │       └── mart_zone_performance.sql
│   ├── seeds/
│   │   └── taxi_zones.csv      # 265 NYC taxi zones
│   ├── tests/
│   │   └── assert_positive_total_amount.sql
│   ├── packages.yml
│   └── dbt_project.yml
├── sql/
│   ├── create_external_tables.sql
│   ├── create_native_tables.sql
│   └── explore_yellow.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── .gitignore
```

---

## 🔄 Pipeline Flow

The Airflow DAG runs on the **1st of every month at 6am** with `catchup=True` to backfill all 2019 data:

```
ingest_yellow ──► load_yellow_to_bq ──►
                                        dbt_run ──► dbt_test
ingest_green  ──► load_green_to_bq  ──►
```

---

## 📦 dbt Data Model

### Layered Architecture

```
Raw (BigQuery)
    └── Staging (views)           ← Clean + type cast
            └── Core (tables)     ← Dimensions + Facts
                    └── Marts     ← Business aggregations
```

### Models

| Model | Layer | Type | Rows | Description |
|-------|-------|------|------|-------------|
| `stg_yellow_tripdata` | Staging | View | 84.6M | Cleaned yellow taxi trips |
| `stg_green_tripdata` | Staging | View | 6.3M | Cleaned green taxi trips |
| `dim_zones` | Core | Table | 265 | NYC taxi zone reference |
| `fct_trips` | Core | Incremental | 82.6M | All trips unified + enriched |
| `mart_daily_revenue` | Marts | Table | — | Daily revenue by taxi type |
| `mart_hourly_patterns` | Marts | Table | — | Trip patterns by hour |
| `mart_zone_performance` | Marts | Table | — | Revenue by pickup zone |

### Key Design Decisions

- **Incremental fact table** — only processes new rows on each run, not full 90M reload
- **Partitioned by `pickup_datetime`** — 53% query cost reduction vs full table scan
- **Clustered by `pickup_location_id`, `dropoff_location_id`** — optimizes zone-based queries
- **Surrogate key** via `dbt_utils.generate_surrogate_key` — stable unique trip identifier
- **NUMERIC type for money** — exact precision, avoids floating point rounding errors

---

## ⚙️ Setup & Installation

### Prerequisites

- Docker Desktop with WSL2 integration
- GCP account (free tier sufficient)
- Python 3.11
- uv package manager

### 1. Clone the repository

```bash
git clone https://github.com/Amin-16/nyc-taxi-pipeline.git
cd nyc-taxi-pipeline
```

### 2. GCP Setup

1. Create a GCP project
2. Enable BigQuery API and Cloud Storage API
3. Create a service account with roles:
   - `Storage Admin`
   - `BigQuery Data Editor`
   - `BigQuery Job User`
4. Download JSON key → save as `gcp-creds.json` in project root
5. Create GCS bucket: `nyc-taxi-datalake-{your-project-id}`
6. Create BigQuery datasets in `us-east1`:
   - `nyc_taxi_raw`
   - `nyc_taxi_staging`
   - `nyc_taxi_marts`

### 3. Environment Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create Python 3.11 virtual environment
uv venv --python 3.11
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your GCP project ID and bucket name
```

### 5. Start Airflow

```bash
# Fix permissions
sudo chown -R 50000:0 logs

# Initialize database
docker compose up airflow-init

# Start services
docker compose up airflow-webserver airflow-scheduler -d
```

Visit `http://localhost:8080` (admin/admin)

### 6. Configure Airflow

In Airflow UI → Admin → Variables:
- `GCS_BUCKET` = `nyc-taxi-datalake-{your-project-id}`
- `GCP_PROJECT_ID` = `{your-project-id}`

In Airflow UI → Admin → Connections:
- Add `google_cloud_default` → Google Cloud → keyfile path

### 7. Run dbt

```bash
cd nyc_taxi
dbt deps
dbt seed
dbt run
dbt test
```

### 8. Trigger the pipeline

Enable and trigger `nyc_taxi_pipeline` DAG in Airflow UI.

---

## 🧪 Data Quality

### dbt Tests
- `not_null` on all key columns
- `unique` on surrogate keys
- `accepted_values` on payment_type, taxi_type
- `accepted_range` on fare_amount, trip_distance
- Custom singular test: no future trip timestamps

### Data Issues Found & Handled
- **Schema drift** — `ehail_fee` column changed type across monthly files → enforced consistent schema at ingestion using pandas dtypes
- **Dirty timestamps** — 1,442 rows with invalid dates (year 2001, 2090) → filtered in dbt staging layer
- **Zero/negative fares** — filtered in staging (`total_amount > 0`)

---

## 💡 Key Engineering Decisions

| Decision | Rationale |
|----------|-----------|
| Schema enforcement at ingestion | Prevent type conflicts in BigQuery external tables |
| Idempotent ingestion | Safe to re-run — skips already uploaded files |
| External tables as reference layer | Zero storage cost, audit trail of raw files |
| Month-by-month BQ loading | Avoids cross-file schema conflicts with autodetect |
| ELT over ETL | Transform in BigQuery using dbt — leverage cloud compute |
| Incremental dbt models | Process only new data — 90M rows → ~300K new rows/month |

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Total rows processed | 90,899,429 |
| Raw data size | ~900 MB |
| Fact table size | 10.8 GiB (processed) |
| dbt run time (first load) | ~16 seconds |
| Query cost reduction (partitioning) | 53% |
| Data quality (valid rows) | 99.998% |

---

## 🔮 Future Improvements

- Add Great Expectations for advanced data quality checks
- Implement Looker Studio dashboard on top of mart models
- Extend to 2020 data to show COVID impact analysis
- Add dbt documentation site deployment via GitHub Actions
- Migrate to Apache Iceberg for schema evolution support

---

## 👤 Author

**Mohamed Amin**
- GitHub: [@Amin-16](https://github.com/Amin-16)

---

## 📄 License

MIT License