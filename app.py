import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Churn Detection", page_icon="🎯", layout="wide")

st.title("🎯 Customer Churn Detection System")
st.markdown("**Identify at-risk B2B customers automatically using ML**")

try:
    with open('churn_report.json') as f:
        data = json.load(f)
except:
    st.error("Error loading data")
    st.stop()

st.header("📊 Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", data['summary']['total_customers'])
col2.metric("🔴 High Risk", data['summary']['high_risk_count'])
col3.metric("🟠 Medium Risk", data['summary']['medium_risk_count'])
col4.metric("Avg Risk Score", f"{data['summary']['avg_risk_score']:.1f}/100")

st.header("🔴 High-Risk Customers")
if data['high_risk_customers']:
    high_risk_df = pd.DataFrame(data['high_risk_customers'])
    st.dataframe(high_risk_df[['customer_id', 'churn_risk_score', 'risk_level', 'spending_trend']].sort_values('churn_risk_score', ascending=False), use_container_width=True)

st.header("💡 Retention Strategies")
if data['retention_strategies']:
    strategies_df = pd.DataFrame(data['retention_strategies'])
    st.dataframe(strategies_df[['customer_id', 'risk_score', 'recommended_discount_pct', 'action']].sort_values('risk_score', ascending=False), use_container_width=True)

st.header("📈 All Customers")
try:
    metrics = pd.read_csv('reports/customer_metrics.csv')
    st.dataframe(metrics.sort_values('churn_risk_score', ascending=False), use_container_width=True)
except:
    st.error("Error loading metrics")

st.header("📦 Product Analysis")
try:
    product_risk = pd.read_csv('reports/product_risk_analysis.csv')
    st.dataframe(product_risk.nsmallest(20, 'quantity_change_pct'), use_container_width=True)
except:
    st.error("Error loading product analysis")
```

5. Click **"Commit new file"**

---

## 🎯 **THEN: Deploy to Streamlit Cloud**

1. Go to **share.streamlit.io**
2. Click **"Sign in with GitHub"**
3. Click **"New app"**
4. Fill in:
   - **GitHub repo:** https://github.com/ROSI9979/supplier-churn-detection
   - **Branch:** main
   - **File path:** app.py
5. Click **"Deploy"**
6. Wait 2-3 minutes

**Your live URL will be:**
```
https://share.streamlit.io/ROSI9979/supplier-churn-detection
