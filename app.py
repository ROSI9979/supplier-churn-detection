import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Churn Detection Dashboard", page_icon="🎯", layout="wide")

st.markdown("<style>h1 { color: #1e40af; font-size: 2.5rem; font-weight: 700; }h2 { color: #1e40af; font-size: 1.8rem; border-bottom: 3px solid #3b82f6; padding-bottom: 0.5rem; }</style>", unsafe_allow_html=True)

try:
    with open('churn_report.json') as f:
        data = json.load(f)
except:
    st.error("Error loading churn_report.json")
    st.stop()

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🎯 Customer Churn Detection System")
    st.markdown("**AI-Powered B2B Customer Retention Intelligence**")
with col2:
    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

st.divider()

st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("👥 Total Customers", f"{data['summary']['total_customers']}")
with col2:
    st.metric("🔴 High Risk", f"{data['summary']['high_risk_count']}")
with col3:
    st.metric("🟠 Medium Risk", f"{data['summary']['medium_risk_count']}")
with col4:
    st.metric("📊 Avg Risk Score", f"{data['summary']['avg_risk_score']:.1f}")
with col5:
    st.metric("💰 Revenue at Risk", f"£{data['summary']['total_revenue_at_risk']/1000:.0f}K")

st.divider()

st.subheader("🔍 Filters")
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    risk_filter = st.selectbox("Filter by Risk:", ["All", "Critical (70+)", "High (50-70)"], index=0)
with filter_col2:
    sort_by = st.selectbox("Sort by:", ["Revenue", "Risk Score", "Days Until Churn"], index=0)
with filter_col3:
    display_count = st.slider("Show customers:", 3, min(20, len(data['high_risk_customers'])), 8)

high_risk_df = pd.DataFrame(data['high_risk_customers'])

if "Critical" in risk_filter:
    filtered_df = high_risk_df[high_risk_df['churn_risk_score'] >= 70]
elif "High" in risk_filter:
    filtered_df = high_risk_df[(high_risk_df['churn_risk_score'] >= 50) & (high_risk_df['churn_risk_score'] < 70)]
else:
    filtered_df = high_risk_df

if "Revenue" in sort_by:
    filtered_df = filtered_df.sort_values('clv', ascending=False)
elif "Risk" in sort_by:
    filtered_df = filtered_df.sort_values('churn_risk_score', ascending=False)
else:
    filtered_df = filtered_df.sort_values('days_until_churn', ascending=True)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔴 At-Risk Customers", "📊 Analytics", "📦 Products", "💡 Strategies", "⚙️ Settings"])

with tab1:
    st.subheader(f"High-Risk Customers ({len(filtered_df)} found)")
    
    if len(filtered_df) > 0:
        for idx, (_, row) in enumerate(filtered_df.head(display_count).iterrows(), 1):
            if row['churn_risk_score'] >= 85:
                color_code = "#dc2626"
                color_text = "🔴 CRITICAL"
            elif row['churn_risk_score'] >= 75:
                color_code = "#ea580c"
                color_text = "🟠 HIGH"
            else:
                color_code = "#f59e0b"
                color_text = "🟡 MEDIUM"
            
            with st.container():
                col1, col2, col3 = st.columns([1, 5, 2])
                with col1:
                    st.markdown(f"<div style='text-align: center; padding: 1rem; background: {color_code}; border-radius: 10px; color: white;'><h3>{idx}</h3><p>{color_text}</p></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<h4 style='margin: 0; color: #1e40af;'>{row['customer_id']}</h4><p style='margin: 0.5rem 0; color: #666;'>{row.get('business_type', 'Unknown')} • {row.get('region', 'Unknown')}</p>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<h3 style='margin: 0; color: #dc2626;'>£{row.get('clv', 0):,.0f}</h3>", unsafe_allow_html=True)
                
                with st.expander("📋 View Details & Products"):
                    col_a, col_b, col_c, col_d, col_e = st.columns(5)
                    with col_a:
                        st.metric("⏰ Churn In", f"{row.get('days_until_churn', '?')} days")
                    with col_b:
                        st.metric("🎯 Risk", f"{row['churn_risk_score']:.0f}/100")
                    with col_c:
                        st.metric("💰 CLV", f"£{row.get('clv', 0):,.0f}")
                    with col_d:
                        st.metric("📦 Cycle", f"{row.get('purchase_cycle', 30)} days")
                    with col_e:
                        st.metric("📈 ROI", f"{row.get('retention_roi', 0):,.0f}%")
                    
                    st.divider()
                    
                    st.write("**📦 Products at Risk:**")
                    products = ['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items']
                    prod_cols = st.columns(5)
                    for prod_col, product in zip(prod_cols, products):
                        with prod_col:
                            st.markdown(f"<div style='background: #dbeafe; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #3b82f6;'><p style='margin: 0; font-size: 0.9rem;'>📦 {product}</p><p style='margin: 0.5rem 0; color: #dc2626;'>AT RISK</p></div>", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.write("**Customer Info**")
                        st.info(f"📅 Churn: {row.get('predicted_churn_date', 'N/A')}\n📊 Trend: {row.get('spending_trend', 0):.1f}%\n💼 Type: {row.get('business_type', 'N/A')}")
                    with col_y:
                        st.write("**Action Plan**")
                        st.success(f"💰 Discount: {row.get('recommended_discount_pct', 0)}%\n🎯 {row.get('action', 'Monitor')}\n✅ Save 5 products")
                
                st.divider()
    else:
        st.info("✅ No customers in this category")

with tab2:
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Risk Distribution**")
        fig1 = px.histogram(filtered_df, x='churn_risk_score', nbins=15, color_discrete_sequence=['#3b82f6'])
        fig1.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.write("**Top 10 Customers**")
        top_10 = filtered_df.nlargest(10, 'clv')
        fig2 = px.bar(top_10, x='clv', y='customer_id', orientation='h', color='churn_risk_score', color_continuous_scale='Reds')
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("📦 Products at Risk")
    
    products = st.multiselect("Select Products:", ['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items'], 
                             default=['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items'])
    
    if products:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Products", len(products))
        with col2:
            st.metric("👥 Customers", len(filtered_df))
        with col3:
            st.metric("💰 Risk", f"£{filtered_df['clv'].sum():,.0f}")
        
        st.divider()
        
        for product in products:
            col_a, col_b, col_c = st.columns([1, 3, 1])
            with col_a:
                st.markdown(f"<div style='background: #fecaca; padding: 1rem; border-radius: 8px; text-align: center;'><h3 style='margin: 0;'>{len(filtered_df)}</h3><p style='margin: 0; font-size: 0.8rem;'>Customers</p></div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<h4 style='margin: 0;'>📦 {product}</h4><p style='margin: 0.5rem 0; color: #666;'>At risk from {len(filtered_df)} customers</p>", unsafe_allow_html=True)
            with col_c:
                revenue_per_product = filtered_df['clv'].sum() / len(products) if products else 0
                st.markdown(f"<div style='background: #dcfce7; padding: 1rem; border-radius: 8px; text-align: center;'><h3 style='margin: 0; color: #dc2626;'>£{int(revenue_per_product):,}</h3><p style='margin: 0; font-size: 0.8rem;'>Revenue</p></div>", unsafe_allow_html=True)
            st.divider()

with tab4:
    st.subheader("💡 Retention Strategies")
    
    for idx, (_, row) in enumerate(filtered_df.head(5).iterrows(), 1):
        st.markdown(f"<div style='padding: 1rem; background: #f3f4f6; border-radius: 8px; margin: 0.5rem 0;'><h5 style='margin: 0;'>{idx}. {row['customer_id']}</h5><p style='margin: 0.5rem 0;'>💰 Offer {row.get('recommended_discount_pct', 0)}% discount | ⏰ Act in {row.get('days_until_churn', '?')} days | 📈 ROI: {row.get('retention_roi', 0):,.0f}%</p></div>", unsafe_allow_html=True)

with tab5:
    st.subheader("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📊 Customers: {data['summary']['total_customers']}\n🔴 High Risk: {data['summary']['high_risk_count']}\n💰 Revenue at Risk: £{data['summary']['total_revenue_at_risk']:,}")
    with col2:
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "customers.csv", "text/csv", use_container_width=True)

