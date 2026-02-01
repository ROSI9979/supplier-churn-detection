import pandas as pd
import json
from datetime import datetime
from tabulate import tabulate

class ReportGenerator:
    """Generate reports and insights from churn analysis"""
    
    def __init__(self, results_dict):
        self.metrics = results_dict['customer_metrics']
        self.product_risk = results_dict['product_risk']
        self.strategies = results_dict['retention_strategies']
    
    def generate_executive_summary(self):
        """Generate high-level executive summary"""
        
        print("\n" + "="*70)
        print("EXECUTIVE SUMMARY - CUSTOMER CHURN RISK ANALYSIS")
        print("="*70)
        
        total_customers = len(self.metrics)
        high_risk = len(self.metrics[self.metrics['risk_level'] == 'High Risk'])
        medium_risk = len(self.metrics[self.metrics['risk_level'] == 'Medium Risk'])
        low_risk = len(self.metrics[self.metrics['risk_level'] == 'Low Risk'])
        
        avg_risk_score = self.metrics['churn_risk_score'].mean()
        
        print(f"\nTotal Customers Analyzed: {total_customers}")
        print(f"\nRisk Distribution:")
        print(f"  🔴 High Risk:   {high_risk} customers ({high_risk/total_customers*100:.1f}%)")
        print(f"  🟠 Medium Risk: {medium_risk} customers ({medium_risk/total_customers*100:.1f}%)")
        print(f"  🟢 Low Risk:    {low_risk} customers ({low_risk/total_customers*100:.1f}%)")
        
        print(f"\nAverage Risk Score: {avg_risk_score:.1f}/100")
        
        # Financial impact estimate
        high_risk_spending = self.metrics[self.metrics['risk_level'] == 'High Risk']['avg_spending'].sum()
        print(f"\nMonthly Revenue at Risk: £{high_risk_spending:,.2f}")
        print(f"Annual Revenue at Risk: £{high_risk_spending * 12:,.2f}")
    
    def generate_high_risk_report(self):
        """Detailed report on high-risk customers"""
        
        print("\n" + "="*70)
        print("HIGH-RISK CUSTOMERS - DETAILED ANALYSIS")
        print("="*70)
        
        high_risk = self.metrics[self.metrics['risk_level'] == 'High Risk'].copy()
        
        if len(high_risk) == 0:
            print("\n✓ No high-risk customers identified")
            return
        
        # Sort by risk score
        high_risk = high_risk.sort_values('churn_risk_score', ascending=False)
        
        display_cols = ['customer_id', 'churn_risk_score', 'spending_trend', 
                       'recent_vs_historical_pct', 'avg_spending']
        
        print("\n" + tabulate(
            high_risk[display_cols].head(15),
            headers=['Customer', 'Risk Score', 'Spending Trend', 'Recent Change %', 'Avg Monthly £'],
            tablefmt='grid',
            floatfmt='.2f',
            showindex=False
        ))
    
    def generate_product_risk_report(self):
        """Report on which products are being lost"""
        
        print("\n" + "="*70)
        print("PRODUCT-LEVEL CHURN ANALYSIS")
        print("="*70)
        
        if len(self.product_risk) == 0:
            print("\nNo product churn signals detected")
            return
        
        # Find products with largest decline
        declining_products = self.product_risk[
            self.product_risk['quantity_change_pct'] < -30
        ].sort_values('quantity_change_pct')
        
        print(f"\nProducts with Significant Decline (>30%):\n")
        
        product_summary = declining_products.groupby('product').agg({
            'customer_id': 'count',
            'quantity_change_pct': 'mean'
        }).sort_values('quantity_change_pct')
        
        product_summary.columns = ['Customers Affected', 'Avg Decline %']
        
        print(tabulate(
            product_summary,
            headers=['Product', 'Customers Affected', 'Avg Decline %'],
            tablefmt='grid',
            floatfmt='.1f'
        ))
    
    def generate_retention_recommendations(self):
        """Generate actionable retention recommendations"""
        
        print("\n" + "="*70)
        print("RETENTION STRATEGY RECOMMENDATIONS")
        print("="*70)
        
        if len(self.strategies) == 0:
            print("\n✓ No high-risk customers requiring immediate action")
            return
        
        urgent = self.strategies[self.strategies['priority'] == 'URGENT']
        high = self.strategies[self.strategies['priority'] == 'HIGH']
        
        print(f"\n🔴 URGENT Actions ({len(urgent)} customers):")
        print(f"   Recommended discount: {urgent['recommended_discount_pct'].iloc[0] if len(urgent) > 0 else 'N/A'}%\n")
        
        if len(urgent) > 0:
            for _, row in urgent.head(5).iterrows():
                print(f"   • {row['customer_id']}")
                print(f"     Risk Score: {row['risk_score']:.1f}/100")
                print(f"     At-Risk Products: {row['products_at_risk']}")
                print(f"     Action: {row['action']}\n")
        
        if len(high) > 0:
            print(f"\n🟠 HIGH Priority Actions ({len(high)} customers):")
            print(f"   Recommended discount: {high['recommended_discount_pct'].iloc[0]}%\n")
            
            for _, row in high.head(5).iterrows():
                print(f"   • {row['customer_id']}")
                print(f"     Action: {row['action']}\n")
    
    def generate_metrics_report(self):
        """Detailed metrics for all customers"""
        
        print("\n" + "="*70)
        print("CUSTOMER METRICS - ALL CUSTOMERS")
        print("="*70)
        
        display_df = self.metrics[[
            'customer_id', 'avg_spending', 'spending_trend',
            'recent_vs_historical_pct', 'churn_risk_score', 'risk_level'
        ]].sort_values('churn_risk_score', ascending=False)
        
        print("\n" + tabulate(
            display_df.head(20),
            headers=['Customer', 'Avg Spending', 'Trend', 'Recent Change %', 'Risk Score', 'Risk Level'],
            tablefmt='grid',
            floatfmt='.2f',
            showindex=False
        ))
        
        if len(display_df) > 20:
            print(f"\n... and {len(display_df) - 20} more customers")
    
    def export_to_csv(self, output_dir='reports'):
        """Export reports to CSV files"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Export customer metrics
        self.metrics.to_csv(f'{output_dir}/customer_metrics.csv', index=False)
        print(f"✓ Exported customer metrics to {output_dir}/customer_metrics.csv")
        
        # Export product risk
        self.product_risk.to_csv(f'{output_dir}/product_risk_analysis.csv', index=False)
        print(f"✓ Exported product risk analysis to {output_dir}/product_risk_analysis.csv")
        
        # Export retention strategies
        self.strategies.to_csv(f'{output_dir}/retention_strategies.csv', index=False)
        print(f"✓ Exported retention strategies to {output_dir}/retention_strategies.csv")
        
        return output_dir
    
    def export_to_json(self, output_file='churn_report.json'):
        """Export complete analysis to JSON"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_customers': len(self.metrics),
                'high_risk_count': len(self.metrics[self.metrics['risk_level'] == 'High Risk']),
                'medium_risk_count': len(self.metrics[self.metrics['risk_level'] == 'Medium Risk']),
                'avg_risk_score': float(self.metrics['churn_risk_score'].mean())
            },
            'high_risk_customers': self.metrics[
                self.metrics['risk_level'] == 'High Risk'
            ].to_dict('records'),
            'retention_strategies': self.strategies.to_dict('records')
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✓ Exported complete report to {output_file}")
    
    def generate_full_report(self, export_csv=True, export_json=True):
        """Generate complete analysis report"""
        
        self.generate_executive_summary()
        self.generate_high_risk_report()
        self.generate_product_risk_report()
        self.generate_retention_recommendations()
        self.generate_metrics_report()
        
        print("\n" + "="*70)
        
        if export_csv:
            self.export_to_csv()
        
        if export_json:
            self.export_to_json()
        
        print("\n✓ Report generation complete!")


if __name__ == "__main__":
    # This will be called from main.py
    pass
