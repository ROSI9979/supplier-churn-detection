import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class ChurnDetectionModel:
    """Detect customers at risk of churning using multiple techniques"""
    
    def __init__(self, anomaly_threshold=-0.5):
        self.anomaly_threshold = anomaly_threshold
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.2, random_state=42)
        self.customer_profiles = None
    
    def prepare_customer_metrics(self, df):
        """Calculate key metrics for each customer per month"""
        
        # Monthly spending by customer
        monthly_spend = df.groupby(['customer_id', 'month']).agg({
            'total_value': 'sum',
            'quantity': 'sum',
            'product': 'count'  # number of SKUs purchased
        }).reset_index()
        
        monthly_spend.columns = ['customer_id', 'month', 'spending', 'total_quantity', 'num_products']
        
        # Calculate trend metrics for each customer
        customer_metrics = []
        
        for customer in df['customer_id'].unique():
            customer_data = monthly_spend[monthly_spend['customer_id'] == customer].sort_values('month')
            
            if len(customer_data) < 2:
                continue
            
            spending_values = customer_data['spending'].values
            months = customer_data['month'].values
            
            # Calculate trend using linear regression
            z = np.polyfit(months, spending_values, 1)
            trend_slope = z[0]  # Negative slope = decreasing spend
            
            # Calculate volatility
            spending_std = spending_values.std()
            spending_mean = spending_values.mean()
            
            # Recent vs historical average
            recent_avg = spending_values[-3:].mean() if len(spending_values) >= 3 else spending_values.mean()
            historical_avg = spending_values[:-3].mean() if len(spending_values) > 3 else spending_values.mean()
            
            # Calculate percentage change
            pct_change = ((recent_avg - historical_avg) / (historical_avg + 1)) * 100
            
            # Number of months with zero spending
            zero_months = (spending_values == 0).sum()
            
            customer_metrics.append({
                'customer_id': customer,
                'avg_spending': spending_mean,
                'spending_trend': trend_slope,
                'spending_volatility': spending_std,
                'recent_vs_historical_pct': pct_change,
                'zero_spending_months': zero_months,
                'total_months': len(spending_values),
                'latest_spending': spending_values[-1],
                'first_spending': spending_values[0]
            })
        
        return pd.DataFrame(customer_metrics)
    
    def detect_churn_risk(self, metrics_df):
        """Score customers for churn risk using multiple indicators"""
        
        # Initialize risk score
        metrics_df['churn_risk_score'] = 0
        
        # 1. Trend-based scoring (negative trend = risk)
        trend_scores = stats.zscore(metrics_df['spending_trend'].fillna(0))
        metrics_df['trend_risk'] = np.where(trend_scores < -0.5, abs(trend_scores), 0)
        
        # 2. Recent decline scoring
        recent_decline_scores = stats.zscore(metrics_df['recent_vs_historical_pct'].fillna(0))
        metrics_df['decline_risk'] = np.where(recent_decline_scores < -0.5, abs(recent_decline_scores), 0)
        
        # 3. Zero spending months (strong indicator)
        metrics_df['inactivity_risk'] = metrics_df['zero_spending_months'] * 0.5
        
        # 4. Volatility risk (erratic behavior = potential churn)
        volatility_scores = stats.zscore(metrics_df['spending_volatility'].fillna(0))
        metrics_df['volatility_risk'] = np.where(volatility_scores > 1, volatility_scores, 0)
        
        # Combine into final churn risk score (0-100)
        weights = {
            'trend_risk': 0.35,
            'decline_risk': 0.35,
            'inactivity_risk': 0.20,
            'volatility_risk': 0.10
        }
        
        metrics_df['churn_risk_score'] = (
            metrics_df['trend_risk'] * weights['trend_risk'] +
            metrics_df['decline_risk'] * weights['decline_risk'] +
            metrics_df['inactivity_risk'] * weights['inactivity_risk'] +
            metrics_df['volatility_risk'] * weights['volatility_risk']
        )
        
        # Normalize to 0-100 scale
        max_score = metrics_df['churn_risk_score'].max()
        if max_score > 0:
            metrics_df['churn_risk_score'] = (metrics_df['churn_risk_score'] / max_score) * 100
        
        metrics_df['churn_risk_score'] = metrics_df['churn_risk_score'].round(2)
        
        # Classify risk level
        metrics_df['risk_level'] = pd.cut(
            metrics_df['churn_risk_score'],
            bins=[0, 30, 60, 100],
            labels=['Low Risk', 'Medium Risk', 'High Risk'],
            include_lowest=True
        )
        
        return metrics_df.sort_values('churn_risk_score', ascending=False)
    
    def identify_at_risk_products(self, df, at_risk_customers):
        """Identify which products are being lost to competitors"""
        
        at_risk_ids = at_risk_customers['customer_id'].values
        
        # For at-risk customers, find products with declining purchases
        at_risk_data = df[df['customer_id'].isin(at_risk_ids)].copy()
        
        product_risk = []
        
        for customer in at_risk_ids:
            customer_data = at_risk_data[at_risk_data['customer_id'] == customer]
            
            for product in customer_data['product'].unique():
                product_data = customer_data[customer_data['product'] == product].sort_values('month')
                
                if len(product_data) > 2:
                    quantities = product_data['quantity'].values
                    recent_qty = quantities[-2:].mean()
                    historical_qty = quantities[:-2].mean()
                    
                    if historical_qty > 0:
                        qty_change_pct = ((recent_qty - historical_qty) / historical_qty) * 100
                        
                        product_risk.append({
                            'customer_id': customer,
                            'product': product,
                            'historical_avg_qty': historical_qty,
                            'recent_avg_qty': recent_qty,
                            'quantity_change_pct': qty_change_pct,
                            'last_purchase_qty': quantities[-1]
                        })
        
        return pd.DataFrame(product_risk)
    
    def generate_retention_strategy(self, at_risk_df, product_risk_df):
        """Generate specific retention strategies for at-risk customers"""
        
        strategies = []
        
        for _, customer in at_risk_df.iterrows():
            customer_id = customer['customer_id']
            risk_level = customer['risk_level']
            risk_score = customer['churn_risk_score']
            
            # Get products with declining purchases
            lost_products = product_risk_df[
                (product_risk_df['customer_id'] == customer_id) &
                (product_risk_df['quantity_change_pct'] < -20)
            ]
            
            if len(lost_products) > 0:
                discount_recommendation = self._calculate_discount(risk_score)
                
                strategies.append({
                    'customer_id': customer_id,
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'products_at_risk': ', '.join(lost_products['product'].unique()),
                    'recommended_discount_pct': discount_recommendation,
                    'action': f"Proactive outreach with {discount_recommendation}% discount on lost products",
                    'priority': 'URGENT' if risk_score > 70 else 'HIGH' if risk_score > 50 else 'MEDIUM'
                })
        
        return pd.DataFrame(strategies).sort_values('risk_score', ascending=False)
    
    def _calculate_discount(self, risk_score):
        """Calculate recommended discount based on risk"""
        if risk_score > 75:
            return 15
        elif risk_score > 60:
            return 12
        elif risk_score > 45:
            return 8
        else:
            return 5


def run_churn_detection(transactions_df):
    """Complete pipeline: load data -> detect churn -> generate strategies"""
    
    print("\n" + "="*60)
    print("SUPPLIER CHURN DETECTION SYSTEM")
    print("="*60)
    
    model = ChurnDetectionModel()
    
    # Step 1: Prepare metrics
    print("\n[1/4] Preparing customer metrics...")
    metrics = model.prepare_customer_metrics(transactions_df)
    print(f"✓ Calculated metrics for {len(metrics)} customers")
    
    # Step 2: Detect churn risk
    print("\n[2/4] Detecting churn risk...")
    at_risk_customers = model.detect_churn_risk(metrics)
    high_risk = at_risk_customers[at_risk_customers['risk_level'] == 'High Risk']
    print(f"✓ Identified {len(high_risk)} high-risk customers")
    
    # Step 3: Identify at-risk products
    print("\n[3/4] Identifying products being lost...")
    product_risk = model.identify_at_risk_products(transactions_df, at_risk_customers)
    print(f"✓ Found {len(product_risk)} product-level churn signals")
    
    # Step 4: Generate strategies
    print("\n[4/4] Generating retention strategies...")
    strategies = model.generate_retention_strategy(high_risk, product_risk)
    print(f"✓ Generated {len(strategies)} retention recommendations")
    
    return {
        'customer_metrics': at_risk_customers,
        'product_risk': product_risk,
        'retention_strategies': strategies
    }


if __name__ == "__main__":
    # Example usage
    df = pd.read_csv('transactions.csv')
    results = run_churn_detection(df)
    
    print("\n\nHIGH-RISK CUSTOMERS:")
    print(results['customer_metrics'][results['customer_metrics']['risk_level'] == 'High Risk'][
        ['customer_id', 'churn_risk_score', 'spending_trend', 'recent_vs_historical_pct', 'risk_level']
    ])
