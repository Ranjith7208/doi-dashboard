# BPX Energy - DOI Dashboard

Interactive Division of Interest Work Item Analytics Dashboard built with Streamlit.

## Features

- **Executive KPIs**: Track total open/closed items, average age, and overdue items
- **Interactive Filters**: Filter by status, analyst, priority, and category
- **Analyst Workload**: Monitor team member workload and identify bottlenecks
- **Risk Analysis**: Visualize risk levels and aging buckets
- **Data Export**: Download filtered data as CSV

## Local Testing

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run doi_dashboard_app.py
```

3. Open your browser to `http://localhost:8501`

## Deployment to Streamlit Cloud

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click "New repository"
3. Name it: `doi-dashboard`
4. Set to Public
5. Click "Create repository"

### Step 2: Push Code to GitHub

```bash
cd c:\Users\ranji\Documents
git init
git add doi_dashboard_app.py requirements.txt README.md
git commit -m "Initial commit: DOI Dashboard Streamlit app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/doi-dashboard.git
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/doi-dashboard`
5. Set main file path: `doi_dashboard_app.py`
6. Click "Deploy!"

Your app will be live at: `https://YOUR_USERNAME-doi-dashboard.streamlit.app`

## Data Model

The dashboard uses a dimensional data model:
- **Fact Table**: DOI Work Items
- **Dimensions**: Analysts, Statuses, Priorities, Categories
- **Metrics**: Days Open, Aging Buckets, Risk Levels, Overdue Status

## Key Metrics

- **Days Open**: How long an item has been in the system
- **Aging Buckets**: 0-30, 31-60, 61-90, 90+ days
- **Risk Levels**: CRITICAL, HIGH, MEDIUM, LOW, HEALTHY
- **Overdue Status**: Items past their due date

## Evolution Path

This is v1.0 using sample data. Future enhancements:
- **v2.0**: Connect to Snowflake data warehouse
- **v3.0**: Real-time alerts and automated escalations

## Support

For questions or issues, contact the Land/DOI team.

---

*Demo v1.0 - BPX Energy*
