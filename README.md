### Amazon Review Sentiment Analytics Pipeline

An end-to-end data engineering and analytics project that processes 72,500+ Amazon product reviews using Snowflake, Cortex AI, dbt, and Streamlit — from raw CSV to interactive dashboard.

![Pipeline](https://img.shields.io/badge/Pipeline-Snowflake%20%7C%20dbt%20%7C%20Cortex%20AI%20%7C%20Streamlit-blue)
![Status](https://img.shields.io/badge/Status-Complete-green)
![Tests](https://img.shields.io/badge/dbt%20Tests-9%20Passing-brightgreen)

---

## 🎯 Problem Statement

Star ratings alone don’t tell the full story. A customer might give 5 stars but write a frustrated review, or give 1 star but describe a mostly positive experience. This project uses AI to analyze the actual text of reviews and detect true customer sentiment — then surfaces insights through a transformation pipeline and interactive dashboard.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Kaggle CSV — 72,500 reviews                                      │
│       │                                                          │
│       ▼                                                          │
│  Snowflake: REVIEW_ANALYTICS.RAW.AMAZON_REVIEWS                   │
│       │                                                          │
│       ▼                                                          │
│  Cortex AI: SENTIMENT() — NLP scoring                            │
│       │                                                          │
│       ▼                                                          │
│  REVIEW_ANALYTICS.RAW.REVIEWS_WITH_SENTIMENT                     │
│       │                                                          │
│       ▼                                                          │
│  dbt: staging layer — cleans, parses, casts                        │
│       │                                                          │
│       ├──▶ mart_department_summary                               │
│       ├──▶ mart_subdepartment_summary                            │
│       └──▶ mart_monthly_trends                                   │
│                │                                                  │
│                ▼                                                  │
│  Streamlit Dashboard — 5 interactive tabs                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- Snowflake
- Snowflake Cortex AI
- dbt (Data Build Tool)
- Streamlit in Snowflake
- SQL
- Python

---

## 📁 Project Structure

```
amazon-review-sentiment-analytics/
├── README.md
├── .gitignore
├── sql/
│   ├── 01_create_database.sql        # Database & schema setup
│   ├── 02_sentiment_analysis.sql     # Cortex AI sentiment scoring
│   └── 03_analytics_queries.sql      # Ad-hoc analysis queries
├── review_analytics_dbt/             # dbt transformation project
│   ├── dbt_project.yml               # Project configuration
│   ├── profiles.yml                  # Snowflake connection
│   └── models/
│       ├── sources.yml               # Source declarations
│       ├── schema.yml                # Tests & documentation (9 tests)
│       ├── staging/
│       │   └── stg_reviews.sql       # Data cleaning & type casting
│       └── marts/
│           ├── mart_department_summary.sql
│           ├── mart_subdepartment_summary.sql
│           └── mart_monthly_trends.sql
├── streamlit/
│   └── streamlit_app.py              # 5-tab interactive dashboard
```

---

## 🔑 Key Features

### 1) AI-Powered Sentiment Analysis
- Used `SNOWFLAKE.CORTEX.SENTIMENT()` to analyze 72,500 reviews
- Classified each review as Positive (>0.3), Negative (<-0.3), or Neutral
- No external APIs, no model training — production-ready NLP in one SQL function

### 2) Data Quality Handling
- Detected dirty data (review text in numeric star rating column)
- Parsed unstructured date strings into proper DATE types
- Used `TRY_CAST` and `TRY_TO_DATE` for safe, error-free type conversion
- Filtered invalid rows at the staging layer

### 3) dbt Transformation Pipeline
- Staging layer: cleans, renames, casts, and filters raw data
- Marts layer: pre-aggregated, business-ready tables
- 9 automated data quality tests: uniqueness, not_null, accepted_values
- Dependency management via `{{ ref() }}` and `{{ source() }}`

### 4) Mismatch Detection (Suspicious Reviews)
- Identified 1,351 reviews where star rating contradicts AI sentiment
- 887 cases: High stars (4–5) but negative review text
- 464 cases: Low stars (1–2) but positive review text

### 5) Interactive Dashboard (5 Tabs)
- Overview: sentiment distribution
- By Department: department-level performance
- By Category: sub-department drill-down with filters
- Suspicious Reviews: star-sentiment mismatches
- Trends Over Time: monthly sentiment changes

---

## 📊 Key Findings

| Metric | Value |
|--------|-------|
| Total reviews processed | 72,500 |
| Negative sentiment (AI-detected) | 27,227 (37.5%) |
| Positive sentiment (AI-detected) | 24,294 (33.5%) |
| Neutral/Mixed sentiment | 20,979 (29%) |
| Suspicious reviews detected | 1,351 |
| Worst sentiment category | CellsPhones & Accessories (-0.049) |
| Best sentiment category | Men's Accessories (0.045) |

Notes:
- These figures reflect AI sentiment scoring and data quality checks from the staging/marts layers.

---

## 🚀 How to Reproduce

### Prerequisites
- Snowflake account with Cortex AI access
- Warehouse (XS is sufficient)
- dbt (pre-installed in Snowflake Workspaces)

### Steps

1) Run SQL setup scripts (in Snowflake worksheet)
- Execute sql/01_create_database.sql
- Upload CSV via Snowsight UI → Data → Ingestion
- Execute sql/02_sentiment_analysis.sql

2) Run dbt pipeline (in Snowflake Workspace terminal)
- dbt run --project-dir /review_analytics_dbt      # Builds 4 models
- dbt test --project-dir /review_analytics_dbt     # Runs 9 quality tests

3) Open Streamlit dashboard
- Projects → Streamlit → Create app → Paste streamlit_app.py

Data Quality Tests (example)
- not_null (review_id) -> stg_reviews ✅ PASS
- unique (review_id) -> stg_reviews ✅ PASS
- not_null (star_rating) -> stg_reviews ✅ PASS
- not_null (sentiment_label) -> stg_reviews ✅ PASS
- accepted_values (sentiment_label) -> stg_reviews ✅ PASS
- not_null (department) -> stg_reviews ✅ PASS
- not_null (department) -> mart_department_summary ✅ PASS
- unique (department) -> mart_department_summary ✅ PASS
- not_null (review_date) -> mart_monthly_trends ✅ PASS

Dashboard screenshots
- Several images demonstrating the UI are included in the repository (see README images section)

---

## 📝 Learnings

- Building end-to-end data pipelines on a modern cloud stack
- Using in-warehouse AI/NLP functions for text analysis without ML expertise
- dbt best practices: layered architecture (staging → marts), automated testing, source documentation
- Data quality handling: safe type casting, dirty data detection, graceful error handling
- Dashboard design: progressive disclosure (tabs, filters) for accessibility

---

## 🔮 Future Improvements

- Schedule dbt pipeline with Snowflake Tasks for daily refresh
- Implement incremental models to process only new reviews
- Add topic extraction using Cortex AI to identify specific themes
- Deploy as a Snowflake DBT PROJECT object for production use
- Add data freshness tests and row count monitoring
- Implement alerting for sudden sentiment drops

---

## 👤 Author

Parnika  
Aspiring Data Engineer / Analyst

---

## 📄 Dataset

- Source: Kaggle — Amazon Product Reviews
- Records: 72,500 reviews
- Departments: Computers, Beauty & Personal Care, Electronics, Home & Kitchen, Sports & Outdoors
- Time Range: 2008–2021

---

