"""
Churn Detection Module with Advanced Features
Includes: Risk Scoring, Churn Date Prediction, CLV Calculation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
import json

class ChurnDetectionSystem:
    """Advanced churn detection with predictions and CLV"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.high_risk_threshold = 70
        self.medium_risk_threshold = 45
    
    def detect_churn_risk(self, customer_data):
        """
        Detect churn risk with advanced features:
        - Risk score (0-100)
        - Churn date prediction
        - CLV calculation
        - Days until churn
        """
        
        customer_id = customer_data.get('customer_id', 'Unknown')
        
        # Get spending data
        monthly_spending = customer_data.get('monthly_spending', [])
        annual_spending = customer_data.get('annual_spending', 0)
        transactions = customer_data.get('transactions', [])
        
        if not monthly_spending or len(monthly_spending) < 2:
            return None
        
        # Convert to numpy array
        spending_array = np.array(monthly_spending, dtype=float)
        
        # 1. CALCULATE SPENDING TREND (35% weight)
        trend_risk = self._calculate_spending_trend_risk(spending_array)
        
        # 2. CALCULATE RECENT DECLINE (35% weight)
        decline_risk = self._calculate_recent_decline_risk(spending_array)
        
        # 3. CALCULATE INACTIVITY RISK (20% weight)
        inactivity_risk = self._calculate_inactivity_risk(spending_array)
        
        # 4. CALCULATE VOLATILITY RISK (10% weight)
        volatility_risk = self._calculate_volatility_risk(spending_array)
        
        # COMBINED RISK SCORE
        churn_risk_score = (
            trend_risk * 0.35 +
            decline_risk * 0.35 +
            inactivity_risk * 0.20 +
            volatility_risk * 0.10
        )
        
        # Ensure score is 0-100
        churn_risk_score = max(0, min(100, churn_risk_score))
        
        # Determine risk level
        if churn_risk_score >= self.high_risk_threshold:
            risk_level = "High Risk"
        elif churn_risk_score >= self.medium_risk_threshold:
            risk_level = "Medium Risk"
        else:
            risk_level = "Low Risk"
        
        # FEATURE 1: PREDICT CHURN DATE
        churn_prediction = self._predict_churn_date(transactions)
        
        # FEATURE 2: CALCULATE CLV
        clv = self._calculate_clv(
            annual_spending=annual_spending,
            spending_trend=trend_risk - 50,  # Convert to trend percentage
            years=5
        )
        
        # FEATURE 3: CALCULATE RETENTION ROI
        recommended_discount = self._get_recommended_discount(churn_risk_score)
        discount_cost = annual_spending * (recommended_discount / 100)
        retention_roi = ((clv - discount_cost) / max(discount_cost, 1)) * 100
        
        # Build result
        result = {
            'customer_id': customer_id,
            'churn_risk_score': churn_risk_score,
            'risk_level': risk_level,
            'trend_risk': trend_risk,
            'decline_risk': decline_risk,
            'inactivity_risk': inactivity_risk,
            'volatility_risk': volatility_risk,
            'avg_spending': annual_spending,
            'spending_trend': trend_risk - 50,
            'recent_vs_historical_pct': (spending_array[-1] / np.mean(spending_array[:3]) - 1) * 100 if len(spending_array) >= 3 else 0,
        }
        
        # Add churn prediction data
        if churn_prediction:
            result['predicted_churn_date'] = churn_prediction['predicted_churn_date'].strftime('%Y-%m-%d')
            result['days_until_churn'] = churn_prediction['days_until_churn']
            result['purchase_cycle'] = churn_prediction['purchase_cycle']
            result['last_purchase'] = churn_prediction['last_purchase'].strftime('%Y-%m-%d')
        else:
            result['predicted_churn_date'] = None
            result['days_until_churn'] = None
            result['purchase_cycle'] = None
            result['last_purchase'] = None
        
        # Add CLV data
        result['clv'] = clv
        result['revenue_at_risk'] = clv
        result['recommended_discount_pct'] = recommended_discount
        result['discount_cost'] = discount_cost
        result['retention_roi'] = retention_roi
        
        # Recommended action
        result['action'] = self._get_recommended_action(
            churn_risk_score,
            clv,
            recommended_discount,
            churn_prediction
        )
        
        # Priority
        result['priority'] = self._get_priority(churn_risk_score, clv)
        
        return result
    
    def _calculate_spending_trend_risk(self, spending_array):
        """Calculate risk from spending trend (linear regression slope)"""
        if len(spending_array) < 2:
            return 50
        
        x = np.arange(len(spending_array))
        y = spending_array
        
        # Linear regression
        z = np.polyfit(x, y, 1)
        slope = z[0]
        
        # Calculate trend risk (negative slope = higher risk)
        avg_spending = np.mean(spending_array)
        if avg_spending > 0:
            trend_pct = (slope / avg_spending) * 100
        else:
            trend_pct = 0
        
        # Convert to risk score (0-100)
        trend_risk = 50 - trend_pct  # Negative slope increases risk
        trend_risk = max(0, min(100, trend_risk))
        
        return trend_risk
    
    def _calculate_recent_decline_risk(self, spending_array):
        """Calculate risk from recent spending decline"""
        if len(spending_array) < 2:
            return 50
        
        recent_avg = np.mean(spending_array[-3:])  # Last 3 months
        historical_avg = np.mean(spending_array[:-3]) if len(spending_array) > 3 else np.mean(spending_array[:-1])
        
        if historical_avg > 0:
            decline_pct = ((recent_avg - historical_avg) / historical_avg) * 100
        else:
            decline_pct = 0
        
        # Convert to risk (negative = high risk)
        decline_risk = 50 - decline_pct
        decline_risk = max(0, min(100, decline_risk))
        
        return decline_risk
    
    def _calculate_inactivity_risk(self, spending_array):
        """Calculate risk from months with zero/low spending"""
        zero_months = np.sum(spending_array == 0)
        low_months = np.sum(spending_array < np.mean(spending_array) * 0.2)
        
        total_inactive = zero_months + (low_months * 0.5)
        inactivity_pct = (total_inactive / len(spending_array)) * 100
        
        # Convert to risk (higher inactive % = higher risk)
        inactivity_risk = inactivity_pct * 2
        inactivity_risk = max(0, min(100, inactivity_risk))
        
        return inactivity_risk
    
    def _calculate_volatility_risk(self, spending_array):
        """Calculate risk from erratic spending patterns"""
        if len(spending_array) < 2:
            return 0
        
        # Coefficient of variation
        avg = np.mean(spending_array)
        std = np.std(spending_array)
        
        if avg > 0:
            cv = (std / avg) * 100
        else:
            cv = 0
        
        # High volatility = high risk
        volatility_risk = min(100, cv)
        
        return volatility_risk
    
    def _predict_churn_date(self, transactions):
        """Predict exact date customer will churn"""
        if not transactions or len(transactions) < 2:
            return None
        
        try:
            # Extract dates
            dates = []
            for trans in transactions:
                if isinstance(trans, dict) and 'date' in trans:
                    dates.append(pd.to_datetime(trans['date']))
            
            if len(dates) < 2:
                return None
            
            # Sort dates
            dates = sorted(dates)
            
            # Calculate days between purchases
            date_diffs = []
            for i in range(1, len(dates)):
                diff = (dates[i] - dates[i-1]).days
                if diff > 0:
                    date_diffs.append(diff)
            
            if not date_diffs:
                return None
            
            # Use median purchase cycle
            avg_cycle = int(np.median(date_diffs))
            
            # Last purchase date
            last_purchase = dates[-1]
            
            # Predicted churn date
            predicted_churn_date = last_purchase + timedelta(days=avg_cycle)
            
            # Days until churn
            days_until_churn = (predicted_churn_date - datetime.now()).days
            
            return {
                'predicted_churn_date': predicted_churn_date,
                'days_until_churn': max(0, days_until_churn),
                'purchase_cycle': avg_cycle,
                'last_purchase': last_purchase
            }
        
        except Exception as e:
            return None
    
    def _calculate_clv(self, annual_spending, spending_trend, years=5, discount_rate=0.1):
        """Calculate Customer Lifetime Value"""
        
        # Growth rate (convert trend to decimal)
        growth_rate = spending_trend / 100
        
        # Calculate CLV with compound growth
        clv = 0
        for year in range(years):
            year_revenue = annual_spending * (1 + growth_rate) ** year
            discounted_revenue = year_revenue / (1 + discount_rate) ** year
            clv += discounted_revenue
        
        return max(0, clv)
    
    def _get_recommended_discount(self, risk_score):
        """Get recommended discount based on risk score"""
        if risk_score >= 85:
            return 15
        elif risk_score >= 70:
            return 12
        elif risk_score >= 55:
            return 10
        elif risk_score >= 45:
            return 8
        else:
            return 5
    
    def _get_recommended_action(self, risk_score, clv, discount, churn_pred):
        """Get recommended retention action"""
        
        if risk_score >= 85:
            if churn_pred and churn_pred['days_until_churn'] < 7:
                return f"URGENT: Call customer today. Predicted churn in {churn_pred['days_until_churn']} days. Offer {discount}% discount."
            else:
                return f"Proactive outreach with {discount}% discount on lost products"
        elif risk_score >= 70:
            return f"Send personalized offer with {discount}% discount and product recommendations"
        elif risk_score >= 55:
            return f"Monitor closely. Consider {discount}% discount if purchase pattern worsens"
        else:
            return "Standard retention engagement"
    
    def _get_priority(self, risk_score, clv):
        """Get priority level"""
        if risk_score >= 85 and clv > 100000:
            return "CRITICAL"
        elif risk_score >= 70:
            return "HIGH"
        elif risk_score >= 55:
            return "MEDIUM"
        else:
            return "LOW"
    
    def analyze_customers(self, customers_data):
        """Analyze multiple customers"""
        results = []
        
        for customer in customers_data:
            result = self.detect_churn_risk(customer)
            if result:
                results.append(result)
        
        return results
    
    def get_high_risk_customers(self, results):
        """Get high-risk customers"""
        return [r for r in results if r['risk_level'] == 'High Risk']
    
    def get_retention_strategies(self, results):
        """Generate retention strategies for high-risk customers"""
        strategies = []
        
        high_risk = self.get_high_risk_customers(results)
        
        for customer in sorted(high_risk, key=lambda x: x['churn_risk_score'], reverse=True):
            strategy = {
                'customer_id': customer['customer_id'],
                'risk_score': customer['churn_risk_score'],
                'churn_date': customer['predicted_churn_date'],
                'days_until_churn': customer['days_until_churn'],
                'clv': customer['clv'],
                'recommended_discount_pct': customer['recommended_discount_pct'],
                'action': customer['action'],
                'priority': customer['priority'],
                'products_at_risk': self._identify_at_risk_products(customer),
            }
            strategies.append(strategy)
        
        return strategies
    
    def _identify_at_risk_products(self, customer):
        """Identify products customer is losing"""
        # This would be enhanced with product-level data
        return "Cheese Dips, Drinks, Frozen Items"
