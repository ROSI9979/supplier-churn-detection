import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="Churn Detection Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    h1 { color: #1e40af; font-size: 2.5rem; font-weight: 700; }
    h2 { color: #1e40af; font-size: 1.8rem; border-bottom: 3px solid #3b82f6; padding-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

try:
    with open('churn_report.json') as f:
        data = json.load(f)
    with open('real_food_supplier_data.json') as f:
        customers_data = json.load(f)
except:
    st.error("Error loading data")
    st.stop()

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🎯 Customer Churn Detection System")
    st.markdown("**AI-Powered B2B Customer Retention Intelligence**")
with col2:
    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"), delta=datetime.now().strftime("%Y-%m-%d"))

st.divider()

st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("👥 Total Customers", f"{data['summary']['total_customers']}", delta="Analyzed")
with col2:
    st.metric("🔴 High Risk", f"{data['summary']['high_risk_count']}", delta=f"{data['summary']['high_risk_count']/data['summary']['total_customers']*100:.1f}%", delta_color="inverse")
with col3:
    st.metric("🟠 Medium Risk", f"{data['summary']['medium_risk_count']}", delta="Monitor")
with col4:
    st.metric("📊 Avg Risk Score", f"{data['summary']['avg_risk_score']:.1f}", delta="out of 100")
with col5:
    st.metric("💰 Revenue at Risk", f"£{data['summary']['total_revenue_at_risk']/1000:.0f}K", delta="5-year CLV", delta_color="inverse")

st.divider()

st.subheader("🔍 Advanced Filters & Controls")
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    risk_filter = st.selectbox(
        "📊 Filter by Risk Level:",
        ["🔴 All", "🔴 Critical (70+)", "🟠 High (50-70)", "🟡 Medium (Below 50)"],
        index=0
    )

with filter_col2:
    sort_by = st.selectbox(
        "📈 Sort By:",
        ["💰 Revenue (High to Low)", "🎯 Risk Score (High)", "⏰ Days Until Churn", "📊 Spending"],
        index=0
    )

with filter_col3:
    display_count = st.slider("👥 Show customers:", min_value=3, max_value=min(20, len(data['high_risk_customers'])), value=8)

high_risk_df = pd.DataFrame(data['high_risk_customers'])

if "Critical" in risk_filter:
    filtered_df = high_risk_df[high_risk_df['churn_risk_score'] >= 70]
elif "High (50" in risk_filter:
    filtered_df = high_risk_df[(high_risk_df['churn_risk_score'] >= 50) & (high_risk_df['churn_risk_score'] < 70)]
elif "Below" in risk_filter:
    filtered_df = high_risk_df[high_risk_df['churn_risk_score'] < 50]
else:
    filtered_df = high_risk_df

if "Revenue" in sort_by:
    filtered_df = filtered_df.sort_values('clv', ascending=False)
elif "Risk" in sort_by:
    filtered_df = filtered_df.sort_values('churn_risk_score', ascending=False)
elif "Days" in sort_by:
    filtered_df = filtered_df.sort_values('days_until_churn', ascending=True)
else:
    filtered_df = filtered_df.sort_values('avg_spending', ascending=False)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔴 At-Risk Customers", "📊 Analytics", "📦 Products", "💡 Strategies", "⚙️ Settings"])

with tab1:
    st.subheader(f"High-Risk Customers ({len(filtered_df)} found)")
    
    if len(filtered_df) > 0:
        for idx, (_, row) in enumerate(filtered_df.head(display_count).iterrows(), 1):
            if row['churn_risk_score'] >= 85:
                color = "🔴 CRITICAL"
                color_code = "#dc2626"
            elif row['churn_risk_score'] >= 75:
                color = "🟠 HIGH"
                color_code = "#ea580c"
            else:
                color = "🟡 MEDIUM"
                color_code = "#f59e0b"
            
            with st.container():
                col1, col2, col3 = st.columns([1, 5, 2])
                
                with col1:
                    st.markdown(f"<div style='text-align: center; padding: 1rem; background: {color_code}; border-radius: 10px; color: white;'><h3>{idx}</h3><p>{color}</p></div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"<h4 style='margin: 0; color: #1e40af;'>{row['customer_id']}</h4><p style='margin: 0.5rem 0; color: #666;'>{row.get('business_type', 'Unknown')} • {row.get('region', 'Unknown')}</p>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"<p style='margin: 0; font-size: 0.9rem; color: #666;'>Revenue at Risk</p><h3 style='margin: 0; color: #dc2626;'>£{row.get('clv', 0):,.0f}</h3>", unsafe_allow_html=True)
                
                with st.expander("📋 View Full Details & Products"):
                    det_col1, det_col2, det_col3, det_col4, det_col5 = st.columns(5)
                    with det_col1:
                        st.metric("⏰ Churn In", f"{row.get('days_until_churn', '?')} days")
                    with det_col2:
                        st.metric("🎯 Risk", f"{row['churn_risk_score']:.0f}/100")
                    with det_col3:
                        st.metric("💰 CLV", f"£{row.get('clv', 0):,.0f}")
                    with det_col4:
                        st.metric("📦 Cycle", f"{row.get('purchase_cycle', 30)} days")
                    with det_col5:
                        st.metric("📈 ROI", f"{row.get('retention_roi', 0):,.0f}%")
                    
                    st.divider()
                    
                    # PRODUCTS AT RISK
                    st.write("**📦 Products at Risk of Being Lost:**")
                    
                    # Find customer in original data to get actual products
                    customer_id = row['customer_id']
                    customer_products = []
                    
                    for cust in customers_data:
                        if cust['customer_id'] == customer_id:
                            # Get products from transactions
                            all_products = set()
                            for trans in cust.get('transactions', []):
                                if 'products_ordered' in trans:
                                    all_products.update(trans['products_ordered'])
                            customer_products = list(all_products) if all_products else ['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items']
                            break
                    
                    if not customer_products:
                        customer_products = ['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items']
                    
                    # Display products as badges
                    product_cols = st.columns(len(customer_products))
                    for idx_p, (col_p, product) in enumerate(zip(product_cols, customer_products)):
                        with col_p:
                            st.markdown(f"""
                            <div style='background: #dbeafe; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #3b82f6;'>
                                <p style='margin: 0; font-size: 0.9rem;'>📦 {product}</p>
                                <p style='margin: 0.5rem 0; font-weight: bold; color: #dc2626;'>AT RISK</p>
                                <p style='margin: 0; font-size: 0.8rem; color: #666;'>Annual: £{int(row.get('avg_spending', 0) / len(customer_products)):,}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write("**Customer Info**")
                        st.info(f"📅 Churn Date: {row.get('predicted_churn_date', 'N/A')}\n📊 Trend: {row.get('spending_trend', 0):.1f}%\n💼 Type: {row.get('business_type', 'N/A')}\n📍 Region: {row.get('region', 'N/A')}")
                    with col_b:
                        st.write("**Retention Plan**")
                        st.success(f"💰 Discount: {row.get('recommended_discount_pct', 0)}%\n🎯 Action: {row.get('action', 'Monitor')}\n📦 Save {len(customer_products)} products\n✅ Expected: Retain customer")
                
                st.divider()
    else:
        st.info("✅ No customers in this category")

with tab2:
    st.subheader("📊 Advanced Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Risk Score Distribution**")
        fig1 = px.histogram(filtered_df, x='churn_risk_score', nbins=15, color_discrete_sequence=['#3b82f6'])
        fig1.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.write("**Top 10 by Revenue at Risk**")
        top_10 = filtered_df.nlargest(10, 'clv')
        fig2 = px.bar(top_10, x='clv', y='customer_id', orientation='h', color='churn_risk_score', color_continuous_scale='Reds')
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Churn Timeline**")
        timeline = filtered_df.sort_values('days_until_churn')
        fig3 = px.scatter(timeline, x='days_until_churn', y='clv', size='churn_risk_score', color='churn_risk_score', color_continuous_scale='Reds')
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.write("**Business Type Breakdown**")
        if 'business_type' in filtered_df.columns:
            business_data = filtered_df.groupby('business_type')['clv'].sum().reset_index()
            fig4 = px.pie(business_data, values='clv', names='business_type')
            fig4.update_layout(height=350)
            st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("📦 Product-Level Risk Analysis")
    
    # Aggregate products across all at-risk customers
    all_products_at_risk = {}
    
    for _, customer in filtered_df.iterrows():
        customer_id = customer['customer_id']
        for cust in customers_data:
            if cust['customer_id'] == customer_id:
                for trans in cust.get('transactions', []):
                    if 'products_ordered' in trans:
                        for product in trans['products_ordered']:
                            if product not in all_products_at_risk:
                                all_products_at_risk[product] = {'count': 0, 'revenue': 0}
                            all_products_at_risk[product]['count'] += 1
                            all_products_at_risk[product]['revenue'] += customer.get('avg_spending', 0) / 5
    
    if all_products_at_risk:
        product_df = pd.DataFrame([
            {'Product': prod, 'Customers': data['count'], 'Revenue': data['revenue']}
            for prod, data in all_products_at_risk.items()
        ])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Products at Risk", len(product_df))
        with col2:
            st.metric("👥 Customer Impact", len(filtered_df))
        with col3:
            st.metric("💰 Revenue Impact", f"£{product_df['Revenue'].sum():,.0f}")
        
        st.divider()
        
        st.write("**Products Ranked by Risk Exposure**")
        product_df_sorted = product_df.sort_values('Revenue', ascending=False)
        
        for idx, row_p in product_df_sorted.iterrows():
            col_a, col_b, col_c = st.columns([1, 3, 1])
            with col_a:
                st.markdown(f"<div style='background: #fecaca; padding: 1rem; border-radius: 8px; text-align: center;'><h3 style='margin: 0;'>{row_p['Customers']:.0f}</h3><p style='margin: 0; font-size: 0.8rem;'>Customers</p></div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<h4 style='margin: 0;'>📦 {row_p['Product']}</h4><p style='margin: 0.5rem 0; color: #666;'>At risk from {row_p['Customers']:.0f} customers</p>", unsafe_allow_html=True)
            with col_c:
                st.markdown(f"<div style='background: #dcfce7; padding: 1rem; border-radius: 8px; text-align: center;'><h3 style='margin: 0; color: #dc2626;'>£{row_p['Revenue']:,.0f}</h3><p style='margin: 0; font-size: 0.8rem;'>Revenue</p></div>", unsafe_allow_html=True)
            st.divider()

with tab4:
    st.subheader("💡 Retention Strategies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top 5 Priority Actions**")
        for idx, (_, row) in enumerate(filtered_df.head(5).iterrows(), 1):
            st.markdown(f"<div style='padding: 1rem; background: #f3f4f6; border-radius: 8px; margin: 0.5rem 0;'><h5 style='margin: 0;'>{idx}. {row['customer_id']}</h5><p style='margin: 0.5rem 0; font-size: 0.9rem;'>💰 Discount: {row.get('recommended_discount_pct', 0)}% | ⏰ In {row.get('days_until_churn', '?')} days</p></div>", unsafe_allow_html=True)
    
    with col2:
        st.write("**Expected ROI**")
        roi_data = filtered_df.head(5)[['customer_id', 'retention_roi']].copy()
        fig = px.bar(roi_data, x='customer_id', y='retention_roi', color='retention_roi', color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**About This System**")
        st.info("🎯 AI-Powered Churn Detection\n\n✅ Real-time risk scoring\n✅ Churn date prediction\n✅ CLV calculation\n✅ ROI-based strategies\n✅ Product-level analysis")
    
    with col2:
        st.write("**Performance**")
        st.success(f"📊 Customers: {data['summary']['total_customers']}\n🔴 High Risk: {data['summary']['high_risk_count']}\n💰 Revenue at Risk: £{data['summary']['total_revenue_at_risk']:,}\n📈 Avg Score: {data['summary']['avg_risk_score']:.1f}/100")
    
    st.divider()
    st.write("**Export Data**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 CSV", csv, "customers.csv", "text/csv", use_container_width=True)
    
    with col2:
        json_str = json.dumps(data['high_risk_customers'], indent=2, default=str)
        st.download_button("📥 JSON", json_str, "churn.json", "application/json", use_container_width=True)
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
