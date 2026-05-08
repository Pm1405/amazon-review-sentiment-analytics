# 🛒 Amazon Review Sentiment Analytics Pipeline

An end-to-end data engineering and analytics project that processes 72,500+ Amazon product reviews using **Snowflake**, **Cortex AI**, **dbt**, and **Streamlit** — from raw CSV to interactive dashboard.

![Pipeline](https://img.shields.io/badge/Pipeline-Snowflake%20%7C%20dbt%20%7C%20Cortex%20AI%20%7C%20Streamlit-blue)
![Status](https://img.shields.io/badge/Status-Complete-green)
![Tests](https://img.shields.io/badge/dbt%20Tests-9%20Passing-brightgreen)

---

## 🎯 Problem Statement

Star ratings alone don't tell the full story. A customer might give 5 stars but write a frustrated review, or give 1 star but describe a mostly positive experience. This project uses AI to analyze the actual text of reviews and detect true customer sentiment — then surfaces insights through a transformation pipeline and interactive dashboard.

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────┐ │ DATA PIPELINE │ ├─────────────────────────────────────────────────────────────────┤ │ │ │ [Kaggle CSV — 72,500 reviews] │ │ │ │ │ ▼ │ │ [Snowflake: REVIEW_ANALYTICS.RAW.AMAZON_REVIEWS] │ │ │ │ │ ▼ │ │ [Cortex AI: SENTIMENT() — NLP scoring] │ │ │ │ │ ▼ │ │ [REVIEW_ANALYTICS.RAW.REVIEWS_WITH_SENTIMENT] │ │ │ │ │ ▼ │ │ [dbt: staging layer — cleans, parses, casts] │ │ │ │ │ ├──▶ mart_department_summary │ │ ├──▶ mart_subdepartment_summary │ │ └──▶ mart_monthly_trends │ │ │ │ │ ▼ │ │ [Streamlit Dashboard — 5 interactive tabs] │ │ │ └─────────────────────────────────────────────────────────────────┘

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Snowflake** | Cloud data warehouse (storage + compute) |
| **Snowflake Cortex AI** | NLP sentiment analysis on review text |
| **dbt (Data Build Tool)** | Data transformation, testing, documentation |
| **Streamlit in Snowflake** | Interactive dashboard visualization |
| **SQL** | Data manipulation and analytics |
| **Python** | Dashboard application logic |

---

## 📁 Project Structure
amazon-review-sentiment-analytics/ │ ├── README.md ├── .gitignore │ ├── sql/ │ ├── 01_create_database.sql # Database & schema setup │ ├── 02_sentiment_analysis.sql # Cortex AI sentiment scoring │ └── 03_analytics_queries.sql # Ad-hoc analysis queries │ ├── review_analytics_dbt/ # dbt transformation project │ ├── dbt_project.yml # Project configuration │ ├── profiles.yml # Snowflake connection │ ├── models/ │ │ ├── sources.yml # Source declarations │ │ ├── schema.yml # Tests & documentation (9 tests) │ │ ├── staging/ │ │ │ └── stg_reviews.sql # Data cleaning & type casting │ │ └── marts/ │ │ ├── mart_department_summary.sql │ │ ├── mart_subdepartment_summary.sql │ │ └── mart_monthly_trends.sql │ └── streamlit/ └── streamlit_app.py # 5-tab interactive dashboard

## 🔑 Key Features

### 1. AI-Powered Sentiment Analysis
- Used `SNOWFLAKE.CORTEX.SENTIMENT()` to analyze 72,500 reviews
- Classified each review as Positive (>0.3), Negative (<-0.3), or Neutral
- No external APIs, no model training — production-ready NLP in one SQL function

### 2. Data Quality Handling
- Detected dirty data (review text in numeric star rating column)
- Parsed unstructured date strings into proper DATE types
- Used `TRY_CAST` and `TRY_TO_DATE` for safe, error-free type conversion
- Filtered invalid rows at the staging layer

### 3. dbt Transformation Pipeline
- **Staging layer:** Cleans, renames, casts, and filters raw data
- **Marts layer:** Pre-aggregated, business-ready tables
- **9 automated data quality tests:** uniqueness, not_null, accepted_values
- Dependency management via `{{ ref() }}` and `{{ source() }}`

### 4. Mismatch Detection (Suspicious Reviews)
- Identified **1,351 reviews** where star rating contradicts AI sentiment
- 887 cases: High stars (4-5) but negative review text
- 464 cases: Low stars (1-2) but positive review text
- Applications: fake review detection, QA flagging, customer behavior analysis

### 5. Interactive Dashboard (5 Tabs)
| Tab | Insight | Chart Types |
|-----|---------|-------------|
| 📊 Overview | Overall sentiment distribution | Metrics + Bar chart |
| 🏢 By Department | Department-level performance | Multiple bar charts |
| 📂 By Category | Sub-department drill-down with filters | Bar charts + Dropdown |
| 🔍 Suspicious Reviews | Star-sentiment mismatches | Metrics + Radio filter + Table |
| 📈 Trends Over Time | Monthly sentiment changes | Line charts |

---

## 📊 Key Findings

| Metric | Value |
|--------|-------|
| Total reviews processed | 72,500 |
| Negative sentiment (AI-detected) | 27,227 (37.5%) |
| Positive sentiment (AI-detected) | 24,294 (33.5%) |
| Neutral/Mixed sentiment | 20,979 (29%) |
| Suspicious reviews detected | 1,351 |
| Worst sentiment category | CellPhones & Accessories (-0.049) |
| Best sentiment category | Men's Accessories (0.045) |

---

## 🚀 How to Reproduce

### Prerequisites
- Snowflake account with Cortex AI access
- Warehouse (XS is sufficient)
- dbt (pre-installed in Snowflake Workspaces)

### Steps

```bash
# 1. Run SQL setup scripts (in Snowflake worksheet)
# Execute sql/01_create_database.sql
# Upload CSV via Snowsight UI → Data → Ingestion
# Execute sql/02_sentiment_analysis.sql

# 2. Run dbt pipeline (in Snowflake Workspace terminal)
dbt run --project-dir /review_analytics_dbt      # Builds 4 models
dbt test --project-dir /review_analytics_dbt     # Runs 9 quality tests

# 3. Open Streamlit dashboard
# Projects → Streamlit → Create app → Paste streamlit_app.py
🧪 Data Quality Tests
#	Test	Model	Status
1	not_null (review_id)	stg_reviews	✅ PASS
2	unique (review_id)	stg_reviews	✅ PASS
3	not_null (star_rating)	stg_reviews	✅ PASS
4	not_null (sentiment_label)	stg_reviews	✅ PASS
5	accepted_values (sentiment_label)	stg_reviews	✅ PASS
6	not_null (department)	stg_reviews	✅ PASS
7	not_null (department)	mart_department_summary	✅ PASS
8	unique (department)	mart_department_summary	✅ PASS
9	not_null (review_date)	mart_monthly_trends	✅ PASS
📈 Dashboard Screenshots
Add screenshots of each tab here

📝 Learnings
Building end-to-end data pipelines on a modern cloud stack
Using in-warehouse AI/NLP functions for text analysis without ML expertise
dbt best practices: layered architecture (staging → marts), automated testing, source documentation
Data quality handling: safe type casting, dirty data detection, graceful error handling
Dashboard design: making complex data accessible through progressive disclosure (tabs, filters, plain-English explanations)
🔮 Future Improvements
 Schedule dbt pipeline with Snowflake Tasks (automated daily refresh)
 Implement incremental models for processing only new reviews
 Add topic extraction using Cortex AI (identify specific complaint themes)
 Deploy as a Snowflake DBT PROJECT object for production use
 Add data freshness tests and row count monitoring
 Implement alerting for sudden sentiment drops
👤 Author
Parnika
Aspiring Data Engineer / Analyst


📄 Dataset
Source: Kaggle — Amazon Product Reviews
Records: 72,500 reviews
Departments: Computers, Beauty & Personal Care, Electronics, Home & Kitchen, Sports & Outdoors
Time Range: 2008–2021
