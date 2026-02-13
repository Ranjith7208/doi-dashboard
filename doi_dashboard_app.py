import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="BPX Energy - DOI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
sns.set_style("whitegrid")

# Title
st.title("📊 BPX Energy - DOI Dashboard")
st.markdown("### Division of Interest Work Item Analytics")
st.markdown("---")

# Cache data generation function
@st.cache_data
def generate_sample_data():
    """Generate sample DOI work items data"""
    np.random.seed(42)
    today = pd.Timestamp(datetime.now().date())

    # Create dimension tables
    analysts = pd.DataFrame({
        'AnalystID': [1, 2, 3, 4, 5],
        'AnalystName': ['Sarah Chen', 'Marcus Johnson', 'Elena Vargas', 'James Wilson', 'Priya Patel'],
        'Email': ['s.chen@bpx.com', 'm.johnson@bpx.com', 'e.vargas@bpx.com', 'j.wilson@bpx.com', 'p.patel@bpx.com'],
        'Team': ['Land/DOI', 'Land/DOI', 'Land/DOI', 'Land/DOI', 'Land/DOI'],
    })

    statuses = pd.DataFrame({
        'StatusID': [1, 2, 3, 4],
        'StatusName': ['Open', 'In Progress', 'Pending Review', 'Closed'],
        'StatusCategory': ['Active', 'Active', 'Active', 'Resolved'],
    })

    priorities = pd.DataFrame({
        'PriorityID': [1, 2, 3],
        'PriorityName': ['High', 'Medium', 'Low'],
    })

    categories = pd.DataFrame({
        'CategoryID': [1, 2, 3, 4],
        'CategoryName': ['Title Review', 'Due Diligence', 'Permitting', 'Other'],
    })

    # Generate 72 DOI work items
    items_data = []
    item_id = 10001

    for i in range(72):
        status_dist = [1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        status_id = np.random.choice(status_dist)

        analyst_dist = [1, 1, 1, 2, 2, 2, 2, 3, 4, 5]
        analyst_id = np.random.choice(analyst_dist)

        priority_dist = [1, 2, 2, 2, 3, 3, 3, 3, 3]
        priority_id = np.random.choice(priority_dist)

        created_offset = np.random.randint(-180, 1)
        created_date = today + timedelta(days=created_offset)

        due_offset = np.random.randint(30, 91)
        due_date = created_date + timedelta(days=due_offset)

        closed_date = None
        if status_id == 4:
            days_to_close = np.random.randint(5, 120)
            closed_date = created_date + timedelta(days=days_to_close)

        category_id = np.random.randint(1, 5)
        source = np.random.choice(['OnBase', 'Dynamics', 'OnBase', 'Dynamics', 'OnBase'])

        items_data.append({
            'ItemID': f'DOI-{item_id}',
            'Title': f'DOI Review - Property {item_id - 10000}',
            'Description': f'Division of Interest evaluation for acreage block',
            'Status': statuses[statuses['StatusID'] == status_id]['StatusName'].values[0],
            'Priority': priorities[priorities['PriorityID'] == priority_id]['PriorityName'].values[0],
            'Category': categories[categories['CategoryID'] == category_id]['CategoryName'].values[0],
            'AssignedTo': analysts[analysts['AnalystID'] == analyst_id]['AnalystName'].values[0],
            'CreatedDate': created_date,
            'DueDate': due_date,
            'ClosedDate': closed_date,
            'LastUpdatedDate': closed_date if closed_date else today - timedelta(days=np.random.randint(0, 30)),
            'SourceSystem': source
        })

        item_id += 1

    doi_items = pd.DataFrame(items_data)

    # Calculate derived metrics
    def calculate_days_open(row):
        if pd.isna(row['ClosedDate']):
            return (today - row['CreatedDate']).days
        else:
            return (row['ClosedDate'] - row['CreatedDate']).days

    doi_items['DaysOpen'] = doi_items.apply(calculate_days_open, axis=1)

    def get_aging_bucket(days):
        if days <= 30:
            return '0-30 days'
        elif days <= 60:
            return '31-60 days'
        elif days <= 90:
            return '61-90 days'
        else:
            return '90+ days'

    doi_items['AgingBucket'] = doi_items['DaysOpen'].apply(get_aging_bucket)

    doi_items['IsOverdue'] = (
        (doi_items['DueDate'] < today) &
        (doi_items['Status'] != 'Closed')
    ).astype(int)

    doi_items['DaysOverdue'] = doi_items.apply(
        lambda row: max(0, (today - row['DueDate']).days) if row['IsOverdue'] else 0,
        axis=1
    )

    def get_risk_level(row):
        if row['IsOverdue']:
            return 'CRITICAL'
        elif row['DaysOpen'] > 90:
            return 'HIGH'
        elif row['DaysOpen'] > 60:
            return 'MEDIUM'
        elif row['DaysOpen'] > 30:
            return 'LOW'
        else:
            return 'HEALTHY'

    doi_items['RiskLevel'] = doi_items.apply(get_risk_level, axis=1)

    return doi_items, analysts, today

# Load data
doi_items, analysts, today = generate_sample_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Status filter
status_options = ['All'] + list(doi_items['Status'].unique())
selected_status = st.sidebar.multiselect(
    "Status",
    options=status_options,
    default=['All']
)

# Analyst filter
analyst_options = ['All'] + list(doi_items['AssignedTo'].unique())
selected_analyst = st.sidebar.multiselect(
    "Assigned To",
    options=analyst_options,
    default=['All']
)

# Priority filter
priority_options = ['All'] + list(doi_items['Priority'].unique())
selected_priority = st.sidebar.multiselect(
    "Priority",
    options=priority_options,
    default=['All']
)

# Category filter
category_options = ['All'] + list(doi_items['Category'].unique())
selected_category = st.sidebar.multiselect(
    "Category",
    options=category_options,
    default=['All']
)

# Apply filters
filtered_data = doi_items.copy()

if 'All' not in selected_status:
    filtered_data = filtered_data[filtered_data['Status'].isin(selected_status)]

if 'All' not in selected_analyst:
    filtered_data = filtered_data[filtered_data['AssignedTo'].isin(selected_analyst)]

if 'All' not in selected_priority:
    filtered_data = filtered_data[filtered_data['Priority'].isin(selected_priority)]

if 'All' not in selected_category:
    filtered_data = filtered_data[filtered_data['Category'].isin(selected_category)]

# Executive KPIs
st.subheader("📈 Executive KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

total_open = len(filtered_data[filtered_data['Status'] != 'Closed'])
total_closed = len(filtered_data[filtered_data['Status'] == 'Closed'])
avg_age_open = filtered_data[filtered_data['Status'] != 'Closed']['DaysOpen'].mean() if total_open > 0 else 0
items_90plus = len(filtered_data[(filtered_data['Status'] != 'Closed') & (filtered_data['DaysOpen'] > 90)])
total_overdue = filtered_data['IsOverdue'].sum()

col1.metric("Total Open", total_open, help="Total number of open DOI items")
col2.metric("Total Closed", total_closed, help="Total number of closed DOI items")
col3.metric("Avg Age (Open)", f"{avg_age_open:.1f} days", help="Average age of open items")
col4.metric("Items >90 Days", items_90plus, delta="CRITICAL" if items_90plus > 0 else None, delta_color="inverse")
col5.metric("Overdue Items", total_overdue, delta="ALERT" if total_overdue > 0 else None, delta_color="inverse")

st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Analyst Workload", "📋 Work Items", "📄 Reports"])

with tab1:
    st.subheader("Dashboard Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Status Distribution
        st.markdown("#### Status Distribution")
        status_counts = filtered_data['Status'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#ff6b6b', '#ffd93d', '#6bcf7f', '#4ecdc4']
        ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
               colors=colors[:len(status_counts)], startangle=90)
        ax.set_title('Status Distribution - All DOI Items')
        st.pyplot(fig)
        plt.close()

    with col2:
        # Aging Distribution
        st.markdown("#### Aging Distribution (Open Items)")
        aging_data = filtered_data[filtered_data['Status'] != 'Closed']
        if len(aging_data) > 0:
            aging_counts = aging_data['AgingBucket'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(8, 6))
            colors_age = ['#6bcf7f', '#ffd93d', '#ff9a76', '#ff6b6b']
            bars = ax.barh(aging_counts.index, aging_counts.values, color=colors_age[:len(aging_counts)])
            ax.set_xlabel('Count')
            ax.set_title('Aging Distribution (Open Items)')
            for i, (idx, val) in enumerate(aging_counts.items()):
                ax.text(val + 0.3, i, str(int(val)), va='center')
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No open items to display")

    col3, col4 = st.columns(2)

    with col3:
        # Risk Level Distribution
        st.markdown("#### Risk Level - Open Items")
        open_items = filtered_data[filtered_data['Status'] != 'Closed']
        if len(open_items) > 0:
            risk_data = open_items['RiskLevel'].value_counts()
            risk_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'HEALTHY']
            risk_sorted = risk_data.reindex([r for r in risk_order if r in risk_data.index])

            fig, ax = plt.subplots(figsize=(8, 6))
            colors_risk = ['#d32f2f', '#ff6b6b', '#ffd93d', '#fff176', '#6bcf7f']
            risk_colors = [colors_risk[risk_order.index(r)] for r in risk_sorted.index]
            bars = ax.bar(risk_sorted.index, risk_sorted.values, color=risk_colors)
            ax.set_ylabel('Count')
            ax.set_title('Risk Level - Open Items')
            ax.tick_params(axis='x', rotation=45)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontsize=9)
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No open items to display")

    with col4:
        # Priority vs Aging Heatmap
        st.markdown("#### Priority x Aging Heatmap")
        open_items_heat = filtered_data[filtered_data['Status'] != 'Closed']
        if len(open_items_heat) > 0:
            priority_aging = pd.crosstab(open_items_heat['Priority'], open_items_heat['AgingBucket'])
            priority_order = ['High', 'Medium', 'Low']
            aging_order = ['0-30 days', '31-60 days', '61-90 days', '90+ days']
            priority_aging = priority_aging.reindex(priority_order).reindex(columns=aging_order, fill_value=0)

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(priority_aging, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Count'})
            ax.set_title('Priority x Aging (Where Are High-Priority Items Stuck?)')
            ax.set_xlabel('Aging Bucket')
            ax.set_ylabel('Priority')
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No open items to display")

with tab2:
    st.subheader("👥 Analyst Workload & Accountability")

    open_items = filtered_data[filtered_data['Status'] != 'Closed']

    if len(open_items) > 0:
        # Analyst scoreboard
        analyst_scorecard = open_items.groupby('AssignedTo').agg({
            'ItemID': 'count',
            'DaysOpen': 'mean',
            'IsOverdue': 'sum',
        }).round(1)

        analyst_scorecard.columns = ['Open Items', 'Avg Age (days)', 'Overdue']

        # Add high risk count
        analyst_scorecard['High Risk'] = open_items[
            open_items['RiskLevel'].isin(['CRITICAL', 'HIGH'])
        ].groupby('AssignedTo')['ItemID'].count()
        analyst_scorecard['High Risk'] = analyst_scorecard['High Risk'].fillna(0).astype(int)

        # Health status
        def workload_health(row):
            if row['Open Items'] > 15:
                return '⚠️ OVERLOADED'
            elif row['Overdue'] > 0 or row['High Risk'] > 0:
                return '⚠️ AT RISK'
            else:
                return '✓ HEALTHY'

        analyst_scorecard['Health Status'] = analyst_scorecard.apply(workload_health, axis=1)
        analyst_scorecard = analyst_scorecard.sort_values('Open Items', ascending=False)

        # Display scorecard
        st.dataframe(
            analyst_scorecard,
            use_container_width=True,
            height=400
        )

        # Workload visualization
        st.markdown("#### Workload Distribution")
        workload = open_items.groupby('AssignedTo')['ItemID'].count().sort_values(ascending=True)

        fig, ax = plt.subplots(figsize=(12, 6))
        colors_load = ['#ff6b6b' if v > 15 else '#ffd93d' if v > 10 else '#6bcf7f' for v in workload.values]
        bars = ax.barh(workload.index, workload.values, color=colors_load)
        ax.set_xlabel('Open Items')
        ax.set_title('Analyst Workload Distribution (Red=Overloaded, Yellow=Heavy, Green=Normal)')
        ax.axvline(x=10, color='gray', linestyle='--', alpha=0.6, label='Threshold (10)')
        for i, (analyst, val) in enumerate(workload.items()):
            ax.text(val + 0.3, i, str(int(val)), va='center', fontsize=9)
        ax.legend()
        st.pyplot(fig)
        plt.close()
    else:
        st.info("No open items to display")

with tab3:
    st.subheader("📋 DOI Work Items - Detailed View")

    # Show count
    st.markdown(f"**Showing {len(filtered_data)} items**")

    # Display options
    show_all_columns = st.checkbox("Show all columns", value=False)

    if show_all_columns:
        display_cols = filtered_data.columns.tolist()
    else:
        display_cols = ['ItemID', 'Title', 'Status', 'Priority', 'Category',
                       'AssignedTo', 'DaysOpen', 'AgingBucket', 'RiskLevel',
                       'IsOverdue', 'CreatedDate', 'DueDate']

    # Display data
    st.dataframe(
        filtered_data[display_cols].sort_values('DaysOpen', ascending=False),
        use_container_width=True,
        height=600,
        hide_index=True
    )

    # Download button
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"doi_items_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab4:
    st.subheader("📄 Bottleneck Analysis")

    open_items = filtered_data[filtered_data['Status'] != 'Closed']

    if len(open_items) > 0:
        st.markdown("#### Top 10 Oldest Open Items")
        oldest = open_items.nlargest(10, 'DaysOpen')[
            ['ItemID', 'Title', 'DaysOpen', 'Priority', 'AssignedTo', 'RiskLevel']
        ]

        st.dataframe(oldest, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### Items by Status")
        status_breakdown = filtered_data['Status'].value_counts().sort_values(ascending=False)

        for status, count in status_breakdown.items():
            pct = (count / len(filtered_data)) * 100
            st.markdown(f"**{status}**: {count} items ({pct:.1f}%)")
    else:
        st.info("No open items to display")

# Footer
st.markdown("---")
st.markdown("**Data as of:** " + today.strftime('%Y-%m-%d'))
st.markdown("*Demo v1.0 - BPX Energy Land/DOI Team*")
