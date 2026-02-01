"""
Main orchestration file for Supplier Churn Detection System
Includes Real-Time Alerts (Feature 3)
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np

from data_generator import DataGenerator
from churn_detection import ChurnDetectionSystem
from database import DatabaseManager
from report_generator import ReportGenerator
from alert_system import AlertSystem


def print_banner():
    """Print system banner"""
    print("\n" + "=" * 80)
    print(" " * 15 + "SUPPLIER CHURN DETECTION SYSTEM")
    print(" " * 10 + "End-to-End B2B Customer Retention Solution")
    print("=" * 80)
    print(f"⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def main():
    """Main execution flow"""
    
    print_banner()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: GENERATE DATA
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("STEP 1: GENERATING SAMPLE DATA")
    print("=" * 80)
    
    data_gen = DataGenerator()
    customers_data = data_gen.generate_sample_data(num_customers=50)
    
    print(f"✓ Generated {len(customers_data)} customers with 3,000+ transactions")
    print(f"📊 Sample Data Generated:")
    print(f"   • Customers: {len(customers_data)}")
    print(f"   • Time Period: 12 months")
    print(f"   • Transactions: 3,000+")
    print(f"   • Products: 5 categories\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: RUN CHURN DETECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("STEP 2: RUNNING CHURN DETECTION ANALYSIS")
    print("=" * 80)
    
    churn_system = ChurnDetectionSystem()
    
    print("[1/4] Preparing customer metrics...")
    churn_results = churn_system.analyze_customers(customers_data)
    print(f"✓ Calculated metrics for {len(churn_results)} customers")
    
    print("[2/4] Detecting churn risk with AI predictions...")
    high_risk = churn_system.get_high_risk_customers(churn_results)
    print(f"✓ Identified {len(high_risk)} high-risk customers")
    
    print("[3/4] Generating retention strategies...")
    strategies = churn_system.get_retention_strategies(churn_results)
    print(f"✓ Created {len(strategies)} retention recommendations")
    
    print("[4/4] Calculating CLV and ROI...")
    total_revenue_at_risk = sum([r.get('clv', 0) for r in high_risk])
    print(f"✓ Total revenue at risk: £{total_revenue_at_risk:,.0f}\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: INITIALIZE DATABASE
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("STEP 3: INITIALIZING DATABASE")
    print("=" * 80)
    
    db_manager = DatabaseManager()
    db_manager.init_database()
    print("✓ Database initialized")
    
    db_manager.insert_customer_metrics(churn_results)
    print(f"✓ Stored {len(churn_results)} customer metrics")
    
    db_manager.insert_churn_predictions(churn_results)
    print(f"✓ Stored churn predictions for {len(churn_results)} customers")
    
    db_manager.insert_retention_actions(strategies)
    print("✓ Stored retention strategies\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4: GENERATE REPORTS
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("STEP 4: GENERATING REPORTS")
    print("=" * 80)
    
    report_gen = ReportGenerator()
    
    print("[1/3] Creating customer metrics CSV...")
    report_gen.generate_customer_metrics_report(churn_results)
    print("✓ Created: reports/customer_metrics.csv")
    
    print("[2/3] Creating retention strategies CSV...")
    report_gen.generate_retention_strategies_report(strategies)
    print("✓ Created: reports/retention_strategies.csv")
    
    print("[3/3] Creating product risk analysis CSV...")
    report_gen.generate_product_risk_report(customers_data, churn_results)
    print("✓ Created: reports/product_risk_analysis.csv")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 5: SEND ALERTS (NEW - FEATURE 3)
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 80)
    print("STEP 5: SENDING REAL-TIME ALERTS")
    print("=" * 80)
    
    alert_system = AlertSystem()
    
    # Print alert summary to console
    alert_system.print_alert_summary(high_risk)
    
    # Option 1: Send email alert (requires Gmail setup)
    # Uncomment and configure if you want to send emails
    # alert_system.send_email_alert(
    #     recipient_email="your-email@gmail.com",
    #     high_risk_customers=high_risk,
    #     use_gmail=True
    # )
    
    # Option 2: Print email alert preview to console (for testing)
    print("\nGenerating email alert preview...")
    alert_system.send_email_alert(
        recipient_email="sales-team@company.com",
        high_risk_customers=high_risk,
        use_gmail=False  # Set to True if Gmail is configured
    )
    
    print("✓ Alerts processed\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 6: GENERATE JSON REPORT
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("STEP 6: GENERATING COMPREHENSIVE JSON REPORT")
    print("=" * 80)
    
    summary_stats = {
        'total_customers': len(churn_results),
        'high_risk_count': len(high_risk),
        'medium_risk_count': len([r for r in churn_results if r['risk_level'] == 'Medium Risk']),
        'avg_risk_score': np.mean([r['churn_risk_score'] for r in churn_results]),
        'total_revenue_at_risk': total_revenue_at_risk,
    }
    
    json_report = {
        'generated_at': datetime.now().isoformat(),
        'summary': summary_stats,
        'high_risk_customers': high_risk,
        'retention_strategies': strategies,
    }
    
    with open('churn_report.json', 'w') as f:
        json.dump(json_report, f, indent=2, default=str)
    
    print("✓ Created: churn_report.json\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 7: DISPLAY HIGH-RISK CUSTOMERS
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("STEP 7: HIGH-RISK CUSTOMERS (TOP 10)")
    print("=" * 80 + "\n")
    
    high_risk_sorted = sorted(high_risk, 
                             key=lambda x: x.get('clv', 0), 
                             reverse=True)
    
    print("🔴 High-Risk Customers (Prioritized by CLV):\n")
    
    for idx, customer in enumerate(high_risk_sorted[:10], 1):
        print(f"{idx}. {customer['customer_id']}")
        print(f"   • Risk Score: {customer['churn_risk_score']:.1f}/100")
        print(f"   • Risk Level: {customer['risk_level']}")
        print(f"   • Churn Date: {customer.get('predicted_churn_date', 'Unknown')}")
        print(f"   • Days Until Churn: {customer.get('days_until_churn', '?')} days")
        print(f"   • Annual Spending: £{customer.get('avg_spending', 0):,.0f}")
        print(f"   • 💰 Customer Lifetime Value: £{customer.get('clv', 0):,.0f}")
        print(f"   • 💥 Revenue at Risk: £{customer.get('revenue_at_risk', 0):,.0f}")
        print(f"   • 📈 Retention ROI: {customer.get('retention_roi', 0):,.0f}%")
        print(f"   • Recommended Discount: {customer.get('recommended_discount_pct', 0)}%")
        print(f"   • Discount Cost: £{customer.get('discount_cost', 0):,.0f}")
        print(f"   • Priority: {customer.get('priority', 'Medium')}")
        print(f"   • Action: {customer['action']}")
        print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # SUMMARY STATISTICS
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80 + "\n")
    
    print(f"Total Customers Analyzed: {summary_stats['total_customers']}")
    print(f"High-Risk Customers: {summary_stats['high_risk_count']} ({summary_stats['high_risk_count']/summary_stats['total_customers']*100:.1f}%)")
    print(f"Medium-Risk Customers: {summary_stats['medium_risk_count']}")
    print(f"Average Risk Score: {summary_stats['avg_risk_score']:.1f}/100")
    print(f"\n💰 TOTAL REVENUE AT RISK: £{summary_stats['total_revenue_at_risk']:,.0f}")
    print(f"   (Annual value of high-risk customers)\n")
    
    total_discount_cost = sum([c.get('discount_cost', 0) for c in high_risk])
    total_roi = sum([c.get('retention_roi', 0) for c in high_risk])
    
    print(f"Retention Investment Required: £{total_discount_cost:,.0f}")
    print(f"   (Total discounts to save all high-risk customers)")
    print(f"\nPotential Savings: £{total_revenue_at_risk - total_discount_cost:,.0f}")
    print(f"   (Revenue retained minus discount cost)")
    print(f"\nOverall Retention ROI: {total_roi/len(high_risk) if high_risk else 0:,.0f}%")
    print(f"   (Average ROI across all high-risk customers)\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # COMPLETION
    # ═══════════════════════════════════════════════════════════════════════
    
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 80 + "\n")
    
    print("📁 Output Files:")
    print("   • reports/customer_metrics.csv")
    print("   • reports/product_risk_analysis.csv")
    print("   • reports/retention_strategies.csv")
    print("   • churn_report.json")
    print("   • supplier_churn.db (SQLite database)\n")
    
    print(f"⏱️  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
