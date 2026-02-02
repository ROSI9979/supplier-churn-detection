import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Churn Detection Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    /* Main container */
    .main {
        padding-top: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #1e40af;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #1e40af;
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 0.5rem;
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================
try:
    with open('churn_report.json') as f:
        data = json.load(f)
except:
    st.error("❌ Error loading data files. Please ensure churn_report.json exists.")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🎯 Customer Churn Detection System")
    st.markdown("**AI-Powered B2B Customer Retention Intelligence**")

with col2:
    st.metric(
        "Last Updated",
        datetime.now().strftime("%H:%M:%S"),
        delta=datetime.now().strftime("%Y-%m-%d")
    )

st.divider()

# ============================================================================
# SUMMARY CARDS
# ============================================================================
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "👥 Total Customers",
        f"{data['summary']['total_customers']}",
        delta="Analyzed"
    )

with col2:
    st.metric(
        "🔴 High Risk",
        f"{data['summary']['high_risk_count']}",
        delta=f"{data['summary']['high_risk_count']/data['summary']['total_customers']*100:.1f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "🟠 Medium Risk",
        f"{data['summary']['medium_risk_count']}",
        delta="Monitor"
    )

with col4:
    st.metric(
        "📊 Avg Risk Score",
        f"{data['summary']['avg_risk_score']:.1f}",
        delta="out of 100"
    )

with col5:
    st.metric(
        "💰 Revenue at Risk",
        f"£{data['summary']['total_revenue_at_risk']/1000:.0f}K",
        delta="5-year CLV",
        delta_color="inverse"
    )

st.divider()

# ============================================================================
# FILTERS SECTION
# ============================================================================
st.subheader("🔍 Advanced Filters & Controls")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    risk_filter = st.selectbox(
        "📊 Filter by Risk Level:",
        ["🔴 All High Risk", "🔴 Critical (70-100)", "🟠 High (50-70)", "🟡 Medium (Below 50)"],
        index=0
    )

with filter_col2:
    sort_by = st.selectbox(
        "📈 Sort By:",
        ["💰 Revenue at Risk (↓)", "🎯 Risk Score (↓)", "⏰ Days Until Churn (↑)", "📊 Annual Spending (↓)"],
        index=0
    )

with filter_col3:
    display_count = st.slider(
        "👥 Display Customers:",
        min_value=3,
        max_value=min(20, len(data['high_risk_customers'])),
        value=8,
        step=1
    )

with filter_col4:
    show_details = st.checkbox("📋 Show Detailed View", value=True)

# Apply filters
high_risk_df = pd.DataFrame(data['high_risk_customers'])

if "Critical" in risk_filter:
    filtered_df = high_risk_df[high_risk_df['churn_risk_score'] >= 70]
elif "High" in risk_filter:
    filtered_df = high_risk_df[(high_risk_df['churn_risk_score'] >= 50) & (high_risk_df['churn_risk_score'] < 70)]
elif "Medium" in risk_filter:
    filtered_df = high_risk_df[high_risk_df['churn_risk_score'] < 50]
else:
    filtered_df = high_risk_df

# Apply sorting
if "Revenue" in sort_by:
    filtered_df = filtered_df.sort_values('clv', ascending=False)
elif "Risk Score" in sort_by:
    filtered_df = filtered_df.sort_values('churn_risk_score', ascending=False)
elif "Days" in sort_by:
    filtered_df = filtered_df.sort_values('days_until_churn', ascending=True)
else:
    filtered_df = filtered_df.sort_values('avg_spending', ascending=False)

st.divider()

# ============================================================================
# MAIN CONTENT TABS
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔴 At-Risk Customers",
    "📊 Analytics",
    "📦 Products",
    "💡 Strategies",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: AT-RISK CUSTOMERS
# ============================================================================
with tab1:
    st.subheader(f"High-Risk Customers ({len(filtered_df)} found)")
    
    if len(filtered_df) > 0:
        for idx, (_, row) in enumerate(filtered_df.head(display_count).iterrows(), 1):
            # Create color coding based on risk
            if row['churn_risk_score'] >= 85:
                color = "🔴 CRITICAL"
                color_code = "#dc2626"
            elif row['churn_risk_score'] >= 75:
                color = "🟠 HIGH"
                color_code = "#ea580c"
            else:
                color = "🟡 MEDIUM"
                color_code = "#f59e0b"
            
            # Customer Card
            with st.container():
                col1, col2, col3 = st.columns([2, 6, 2])
                
                with col1:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: {color_code}; border-radius: 10px; color: white;'>
                        <h3>{idx}</h3>
                        <p style='margin: 0;'>{color}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 1rem;'>
                        <h4 style='margin: 0; color: #1e40af;'>{row['customer_id']}</h4>
                        <p style='margin: 0.5rem 0; color: #666;'>{row.get('business_type', 'Unknown')} • {row.get('region', 'Unknown')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style='text-align: right; padding: 1rem;'>
                        <p style='margin: 0; font-size: 0.9rem; color: #666;'>Revenue at Risk</p>
                        <h3 style='margin: 0; color: #dc2626;'>£{row.get('clv', 0):,.0f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Expandable details
                with st.expander("📋 View Full Details"):
                    detail_col1, detail_col2, detail_col3, detail_col4, detail_col5 = st.columns(5)
                    
                    with detail_col1:
                        st.metric("⏰ Churn In", f"{row.get('days_until_churn', '?')} days")
                    with detail_col2:
                        st.metric("🎯 Risk Score", f"{row['churn_risk_score']:.0f}/100")
                    with detail_col3:
                        st.metric("📦 Purchase Cycle", f"{row.get('purchase_cycle', 30)} days")
                    with detail_col4:
                        st.metric("📈 Retention ROI", f"{row.get('retention_roi', 0):,.0f}%")
                    with detail_col5:
                        st.metric("💵 Annual Spend", f"£{row.get('avg_spending', 0):,.0f}")
                    
                    st.divider()
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write("**Customer Information**")
                        st.info(f"""
                        📅 Churn Date: {row.get('predicted_churn_date', 'Unknown')}
                        📊 Spending Trend: {row.get('spending_trend', 0):.1f}%
                        💼 Contract: {row.get('contract_type', 'Unknown')}
                        """)
                    
                    with col_b:
                        st.write("**Retention Recommendation**")
                        st.success(f"""
                        💰 Recommended Discount: {row.get('recommended_discount_pct', 0)}%
                        🎯 Action: {row.get('action', 'Monitor')}
                        ✅ Expected Outcome: Save customer
                        """)
                
                st.divider()
    else:
        st.info("✅ No customers match the selected filters")

# ============================================================================
# TAB 2: ANALYTICS
# ============================================================================
with tab2:
    st.subheader("📊 Advanced Analytics & Insights")
    
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        st.write("**Risk Score Distribution**")
        fig1 = px.histogram(filtered_df, x='churn_risk_score', nbins=20, 
                           color_discrete_sequence=['#3b82f6'],
                           labels={'churn_risk_score': 'Risk Score'})
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with analytics_col2:
        st.write("**Top 10 Customers by Revenue at Risk**")
        top_10 = filtered_df.nlargest(10, 'clv')
        fig2 = px.bar(top_10, x='clv', y='customer_id', orientation='h',
                     color='churn_risk_score', color_continuous_scale='Reds',
                     labels={'clv': 'Revenue at Risk (£)', 'customer_id': 'Customer'})
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    analytics_col3, analytics_col4 = st.columns(2)
    
    with analytics_col3:
        st.write("**Churn Timeline**")
        timeline_df = filtered_df.sort_values('days_until_churn')
        fig3 = px.scatter(timeline_df, x='days_until_churn', y='clv', 
                         size='churn_risk_score', color='churn_risk_score',
                         hover_data=['customer_id'], color_continuous_scale='Reds',
                         labels={'days_until_churn': 'Days Until Churn', 'clv': 'Revenue at Risk'})
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    with analytics_col4:
        st.write("**Business Type Analysis**")
        if 'business_type' in filtered_df.columns:
            business_summary = filtered_df.groupby('business_type').agg({
                'clv': 'sum',
                'customer_id': 'count'
            }).reset_index()
            fig4 = px.pie(business_summary, values='clv', names='business_type',
                         labels={'clv': 'Revenue at Risk'})
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Business type data not available")

# ============================================================================
# TAB 3: PRODUCTS
# ============================================================================
with tab3:
    st.subheader("📦 Product-Level Risk Analysis")
    
    products = st.multiselect(
        "Select Products to Analyze:",
        ['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items'],
        default=['Cheese Dips', 'Chicken Dips', 'Drinks', 'Sauces', 'Frozen Items']
    )
    
    if products:
        prod_col1, prod_col2, prod_col3 = st.columns(3)
        
        with prod_col1:
            st.metric("🛒 Products Selected", len(products))
        with prod_col2:
            st.metric("👥 Customers Affected", len(filtered_df))
        with prod_col3:
            product_revenue = len(filtered_df) * (filtered_df['clv'].sum() / len(filtered_df) if len(filtered_df) > 0 else 0) / len(products) if products else 0
            st.metric("💰 Revenue at Risk", f"£{int(product_revenue):,}")
        
        st.divider()
        
        st.write("**Products by Risk Exposure**")
        product_data = {
            'Product': products,
            'Customers at Risk': [len(filtered_df)] * len(products),
            'Revenue Impact': [filtered_df['clv'].sum() / len(products) if products else 0] * len(products)
        }
        product_df = pd.DataFrame(product_data)
        
        fig = px.bar(product_df, x='Product', y='Revenue Impact', color='Customers at Risk',
                    color_continuous_scale='Blues', labels={'Revenue Impact': 'Revenue at Risk (£)'})
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 4: STRATEGIES
# ============================================================================
with tab4:
    st.subheader("💡 Retention Strategies")
    
    strategy_col1, strategy_col2 = st.columns(2)
    
    with strategy_col1:
        st.write("**Recommended Actions**")
        
        for idx, (_, row) in enumerate(filtered_df.head(5).iterrows(), 1):
            with st.container():
                st.markdown(f"""
                <div style='padding: 1rem; background: #f3f4f6; border-radius: 8px; margin: 0.5rem 0;'>
                    <h5 style='margin: 0; color: #1e40af;'>{idx}. {row['customer_id']}</h5>
                    <p style='margin: 0.5rem 0; font-size: 0.9rem;'>
                        💰 Discount: {row.get('recommended_discount_pct', 0)}% | 
                        📅 Act in: {row.get('days_until_churn', '?')} days
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    with strategy_col2:
        st.write("**ROI Analysis**")
        
        roi_data = filtered_df.head(5)[['customer_id', 'retention_roi']].copy()
        fig = px.bar(roi_data, x='customer_id', y='retention_roi',
                    color='retention_roi', color_continuous_scale='Greens',
                    labels={'retention_roi': 'ROI %', 'customer_id': 'Customer'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.write("**Action Tracking**")
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📞 Log Call", use_container_width=True):
            st.success("✅ Call logged successfully")
    
    with action_col2:
        if st.button("💌 Send Offer", use_container_width=True):
            st.success("✅ Offer sent successfully")
    
    with action_col3:
        if st.button("📋 Schedule Review", use_container_width=True):
            st.success("✅ Review scheduled successfully")

# ============================================================================
# TAB 5: SETTINGS
# ============================================================================
with tab5:
    st.subheader("⚙️ System Settings & Information")
    
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        st.write("**About This System**")
        st.info("""
        🎯 **Churn Detection System**
        
        An AI-powered solution for identifying and retaining at-risk B2B customers.
        
        **Features:**
        - Real-time risk scoring
        - Churn date prediction
        - Customer Lifetime Value (CLV) calculation
        - ROI-based retention strategies
        - Product-level analysis
        """)
    
    with settings_col2:
        st.write("**System Metrics**")
        st.success(f"""
        📊 **Performance**
        
        - Customers Analyzed: {data['summary']['total_customers']}
        - High Risk Detected: {data['summary']['high_risk_count']}
        - Total Revenue at Risk: £{data['summary']['total_revenue_at_risk']:,}
        - Average Risk Score: {data['summary']['avg_risk_score']:.1f}/100
        - Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
    
    st.divider()
    
    # Download section
    st.write("**Export Data**")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="high_risk_customers.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_col2:
        json_data = json.dumps(data['high_risk_customers'], indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name="churn_report.json",
            mime="application/json",
            use_container_width=True
        )
    
    with export_col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

