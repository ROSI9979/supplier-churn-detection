import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Churn Detection", page_icon="🎯", layout="wide")

st.title("🎯 Customer Churn Detection System")
st.markdown("**Identify at-risk B2B customers with AI-powered churn prediction**")

try:
    with open('churn_report.json') as f:
        data = json.load(f)
    with open('reports/customer_metrics.csv') as f:
        metrics_df = pd.read_csv(f)
except:
    st.error("Error loading data files")
    st.stop()

# SECTION 1: SUMMARY
st.header("📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", data['summary']['total_customers'])
col2.metric("🔴 High Risk", data['summary']['high_risk_count'], delta=f"{data['summary']['high_risk_count']/data['summary']['total_customers']*100:.1f}%")
col3.metric("🟠 Medium Risk", data['summary']['medium_risk_count'])
col4.metric("💰 Total Revenue at Risk", f"£{data['summary']['total_revenue_at_risk']:,.0f}")

# SECTION 2: HIGH-RISK CUSTOMERS
st.header("🔴 High-Risk Customers (⏰ Churn Countdown)")

if data['high_risk_customers']:
    high_risk_df = pd.DataFrame(data['high_risk_customers'])
    high_risk_df = high_risk_df.sort_values('churn_risk_score', ascending=False)
    
    for idx, row in high_risk_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("⏰ CHURN IN", f"{row.get('days_until_churn', '?')} days", delta=f"By {row.get('predicted_churn_date', '?')}")
            
            with col2:
                st.metric("🎯 Risk Score", f"{row['churn_risk_score']:.0f}/100", delta=row['risk_level'])
            
            with col3:
                clv = row.get('clv', row.get('avg_spending', 0))
                st.metric("💰 Value at Risk", f"£{clv:,.0f}", delta="CLV")
            
            with col4:
                cycle = row.get('purchase_cycle', '?')
                st.metric("📦 Cycle", f"{cycle} days" if cycle != '?' else cycle, delta="Avg purchase")
            
            with col5:
                roi = row.get('retention_roi', 0)
                st.metric("📈 Retention ROI", f"{roi:,.0f}%", delta="Expected return")
            
            st.write(f"**Customer:** {row['customer_id']}")
            st.write(f"**Annual Spending:** £{row.get('avg_spending', 0):,.0f}")
            st.write(f"**Spending Trend:** {row.get('spending_trend', 0):.1f}%")
            st.write(f"**Recommended Discount:** {row.get('recommended_discount_pct', 0)}%")
            st.write(f"**Action:** {row.get('action', 'Monitor')}")
            st.divider()
else:
    st.info("✅ No high-risk customers detected")

# SECTION 3: PRODUCTS AT RISK
st.header("📦 Products at Risk of Being Lost")

if data['high_risk_customers']:
    products_data = []
    
    for customer in data['high_risk_customers']:
        products = ['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items']
        for product in products:
            products_data.append({
                'Customer': customer['customer_id'],
                'Product': product,
                'Risk Score': customer['churn_risk_score'],
                'Days Until Churn': customer.get('days_until_churn', '?'),
                'Annual Spend at Risk': f"£{customer.get('avg_spending', 0) / len(products):,.0f}",
                'Priority': 'CRITICAL' if customer.get('days_until_churn', 100) <= 15 else 'HIGH'
            })
    
    products_df = pd.DataFrame(products_data)
    
    st.subheader("Products by Risk Priority")
    st.dataframe(
        products_df.sort_values('Risk Score', ascending=False),
        use_container_width=True,
        height=400
    )
    
    st.subheader("📊 Product Risk Summary")
    product_summary = products_df.groupby('Product').size().reset_index(name='Customers at Risk')
    st.bar_chart(product_summary.set_index('Product'))

# SECTION 4: ALL CUSTOMERS METRICS
st.header("📈 All Customers - Detailed Metrics")

try:
    st.subheader("Customer Risk Overview")
    
    risk_filter = st.multiselect(
        "Filter by Risk Level:",
        ['High Risk', 'Medium Risk', 'Low Risk'],
        default=['High Risk', 'Medium Risk', 'Low Risk']
    )
    
    if risk_filter:
        st.dataframe(
            high_risk_df.sort_values('churn_risk_score', ascending=False),
            use_container_width=True,
            height=400
        )
except Exception as e:
    st.error(f"Error loading customer metrics: {e}")

# SECTION 5: KEY INSIGHTS
st.header("💡 Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Days to Churn", 
              f"{high_risk_df['days_until_churn'].mean():.0f} days" if not high_risk_df.empty else "N/A")

with col2:
    st.metric("Highest Risk Customer", 
              f"{high_risk_df.iloc[0]['customer_id']}" if not high_risk_df.empty else "N/A")

with col3:
    st.metric("Largest Account at Risk",
              f"£{high_risk_df['clv'].max():,.0f}" if not high_risk_df.empty else "N/A")

# SECTION 6: RETENTION STRATEGIES
st.header("💡 Recommended Retention Strategies")

if data['high_risk_customers']:
    strategies_df = pd.DataFrame(data['high_risk_customers']).sort_values('churn_risk_score', ascending=False)
    
    st.write("**Top Priority Actions (by customer value):**")
    
    for idx, row in strategies_df.head(5).iterrows():
        with st.expander(f"📌 {row['customer_id']} - Risk: {row['churn_risk_score']:.0f} - Value: £{row.get('clv', 0):,.0f}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Risk Score", f"{row['churn_risk_score']:.1f}/100")
            
            with col2:
                st.metric("Recommended Discount", f"{row.get('recommended_discount_pct', 0)}%")
            
            with col3:
                st.metric("Days to Act", row.get('days_until_churn', '?'))
            
            st.write(f"**Churn Date:** {row.get('predicted_churn_date', 'Unknown')}")
            st.write(f"**Products at Risk:** Cheese Dips, Chicken Dips, Drinks, Sauces, Frozen Items")
            st.write(f"**Recommended Action:** {row.get('action', 'Monitor')}")
            st.write(f"**CLV (Lifetime Value):** £{row.get('clv', 0):,.0f}")
else:
    st.info("No retention strategies needed")

# SECTION 7: SIDEBAR
st.sidebar.header("ℹ️ About This System")
st.sidebar.markdown("""
## How It Works

This system uses **multi-factor risk scoring** to identify at-risk customers:

### Risk Factors
- **Spending Trend** - Linear regression on monthly spending
- **Recent Decline** - Recent vs historical average
- **Inactivity** - Months with zero purchases
- **Volatility** - Erratic buying patterns

### Risk Levels
- **0-44**: Low risk (stable)
- **45-69**: Medium risk (monitor)
- **70-100**: High risk (act now)

### Key Metrics
- **CLV**: Customer Lifetime Value (5-year projection)
- **ROI**: Return on retention investment
- **Churn Date**: Predicted when customer will leave
- **Products**: Which products are at risk
""")

st.sidebar.markdown("---")
st.sidebar.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.write(f"**Data Points:** {data['summary']['total_customers']} customers analyzed")
