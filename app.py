import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Churn Detection", page_icon="🎯", layout="wide")
st.title("🎯 Churn Detection Dashboard")

try:
    with open('churn_report.json') as f:
        data = json.load(f)
except:
    st.error("No data found")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", data['summary']['total_customers'])
col2.metric("High Risk", data['summary']['high_risk_count'])
col3.metric("Medium Risk", data['summary']['medium_risk_count'])
col4.metric("Avg Score", f"{data['summary']['avg_risk_score']:.0f}")

st.subheader("High-Risk Customers")
for c in data['high_risk_customers']:
    st.write(f"**{c['customer_id']}** - Risk: {c['churn_risk_score']:.0f} | Days: {c.get('days_until_churn', '?')} | Value: £{c.get('clv', 0):,}")
