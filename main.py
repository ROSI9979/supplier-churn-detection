#!/usr/bin/env python3
"""
SUPPLIER CHURN DETECTION SYSTEM
Complete end-to-end solution for identifying at-risk B2B customers
and generating retention strategies.

Usage:
    python main.py                      # Run full pipeline
    python main.py --generate-data      # Generate fresh sample data
    python main.py --analyze-only       # Skip data generation
"""

import pandas as pd
import argparse
import os
import sys
from datetime import datetime

from data_generator import TransactionDataGenerator
from churn_detection import ChurnDetectionModel, run_churn_detection
from database import SupplierDatabase
from report_generator import ReportGenerator


class SupplierChurnSystem:
    """Main application class orchestrating the entire system"""
    
    def __init__(self, data_file='transactions.csv', db_file='supplier_churn.db'):
        self.data_file = data_file
        self.db_file = db_file
        self.transactions_df = None
        self.db = None
        self.results = None
    
    def generate_sample_data(self, num_customers=50, months=12):
        """Generate fresh sample transaction data"""
        print("\n" + "="*70)
        print("STEP 1: GENERATING SAMPLE DATA")
        print("="*70)
        
        generator = TransactionDataGenerator(num_customers=num_customers, months=months)
        self.transactions_df = generator.save_data(self.data_file)
        
        print(f"\n📊 Sample Data Generated:")
        print(f"   • Customers: {num_customers}")
        print(f"   • Time Period: {months} months")
        print(f"   • Total Transactions: {len(self.transactions_df)}")
        print(f"   • Products: {self.transactions_df['product'].nunique()}")
    
    def load_data(self):
        """Load transaction data"""
        if not os.path.exists(self.data_file):
            print(f"❌ Data file not found: {self.data_file}")
            print("   Run with --generate-data flag first")
            return False
        
        print(f"\n📂 Loading data from {self.data_file}...")
        self.transactions_df = pd.read_csv(self.data_file)
        print(f"✓ Loaded {len(self.transactions_df)} transactions")
        return True
    
    def run_analysis(self):
        """Execute churn detection analysis"""
        print("\n" + "="*70)
        print("STEP 2: RUNNING CHURN DETECTION ANALYSIS")
        print("="*70)
        
        self.results = run_churn_detection(self.transactions_df)
    
    def initialize_database(self):
        """Initialize and populate database"""
        print("\n" + "="*70)
        print("STEP 3: INITIALIZING DATABASE")
        print("="*70)
        
        # Remove old database if exists
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
            print("✓ Cleared previous database")
        
        self.db = SupplierDatabase(self.db_file)
        
        # Insert data
        self.db.insert_transactions(self.transactions_df)
        self.db.insert_metrics(self.results['customer_metrics'])
        self.db.insert_predictions(self.results['retention_strategies'])
        
        # Print summary
        summary = self.db.get_dashboard_summary()
        print("\n📊 Database Summary:")
        for key, value in summary.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    def generate_reports(self):
        """Generate comprehensive reports"""
        print("\n" + "="*70)
        print("STEP 4: GENERATING REPORTS")
        print("="*70)
        
        reporter = ReportGenerator(self.results)
        reporter.generate_full_report(export_csv=True, export_json=True)
    
    def run_interactive_queries(self):
        """Run interactive database queries"""
        print("\n" + "="*70)
        print("STEP 5: INTERACTIVE QUERY RESULTS")
        print("="*70)
        
        if not self.db:
            return
        
        # High-risk customers
        print("\n🔴 High-Risk Customers (Top 10):")
        high_risk = self.db.get_high_risk_customers().head(10)
        print(high_risk.to_string(index=False))
        
        # Recommendations
        print("\n\n💡 Retention Recommendations:")
        recommendations = self.db.get_retention_recommendations().head(10)
        
        if len(recommendations) > 0:
            for idx, (_, row) in enumerate(recommendations.iterrows(), 1):
                print(f"\n{idx}. {row['customer_id']}")
                print(f"   Priority: {row['priority']}")
                print(f"   Action: {row['action']}")
                print(f"   Discount: {row['recommended_discount_pct']}%")
                print(f"   Products at Risk: {row['products_at_risk']}")
        else:
            print("No recommendations generated")
    
    def save_quick_reference(self):
        """Save a quick reference guide"""
        
        quick_ref = """
SUPPLIER CHURN DETECTION SYSTEM - QUICK REFERENCE
==================================================

RISK SCORING METHODOLOGY:
• Spending Trend (35%): Linear regression on monthly spending
• Recent Decline (35%): Comparison of recent vs historical averages
• Inactivity (20%): Number of months with zero spending
• Volatility (10%): Erratic purchasing patterns

RISK LEVELS:
• 🔴 HIGH RISK (70-100): Immediate action required
  Recommended: 15% discount + personalized outreach
  
• 🟠 MEDIUM RISK (45-69): Monitor closely
  Recommended: 8-12% discount + periodic check-ins
  
• 🟢 LOW RISK (0-44): Stable customers
  Recommended: Standard retention

KEY OUTPUTS:
1. customer_metrics.csv - Full metrics for all customers
2. product_risk_analysis.csv - Which products are being lost
3. retention_strategies.csv - Specific actions per customer
4. churn_report.json - Complete analysis in JSON format

DATABASE TABLES:
• transactions - All customer purchases
• customer_metrics - Calculated churn scores
• churn_predictions - Recommended actions
• retention_actions - History of interventions

TO QUERY THE DATABASE:
from database import SupplierDatabase
db = SupplierDatabase('supplier_churn.db')
high_risk = db.get_high_risk_customers()
recommendations = db.get_retention_recommendations()

NEXT STEPS:
1. Review high-risk customers in churn_report.json
2. Implement retention actions for URGENT priority customers
3. Offer recommended discounts on at-risk products
4. Track outcomes in retention_actions table
5. Re-run analysis monthly to identify new at-risk customers
"""
        
        with open('QUICK_REFERENCE.txt', 'w') as f:
            f.write(quick_ref)
        
        print("✓ Saved quick reference guide to QUICK_REFERENCE.txt")
    
    def run_full_pipeline(self, generate_data=False):
        """Run complete analysis pipeline"""
        
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "  SUPPLIER CHURN DETECTION SYSTEM".center(68) + "█")
        print("█" + "  End-to-End B2B Customer Retention Solution".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        
        print(f"\n⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Generate or load data
            if generate_data:
                self.generate_sample_data(num_customers=50, months=12)
            else:
                if not self.load_data():
                    return False
            
            # Run analysis
            self.run_analysis()
            
            # Database setup
            self.initialize_database()
            
            # Generate reports
            self.generate_reports()
            
            # Interactive queries
            self.run_interactive_queries()
            
            # Save quick reference
            self.save_quick_reference()
            
            print("\n" + "="*70)
            print("✅ ANALYSIS COMPLETE!")
            print("="*70)
            print(f"\n⏱️  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n📁 Output Files:")
            print("   • reports/customer_metrics.csv")
            print("   • reports/product_risk_analysis.csv")
            print("   • reports/retention_strategies.csv")
            print("   • churn_report.json")
            print("   • supplier_churn.db (SQLite database)")
            print("   • QUICK_REFERENCE.txt")
            
            return True
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.db:
                self.db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Supplier Churn Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                      # Run full pipeline with existing data
  python main.py --generate-data      # Generate fresh sample data first
  python main.py --analyze-only       # Skip data generation
        """
    )
    
    parser.add_argument(
        '--generate-data',
        action='store_true',
        help='Generate fresh sample transaction data'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Skip data generation, run analysis only'
    )
    parser.add_argument(
        '--customers',
        type=int,
        default=50,
        help='Number of customers to generate (default: 50)'
    )
    parser.add_argument(
        '--months',
        type=int,
        default=12,
        help='Number of months of data (default: 12)'
    )
    
    args = parser.parse_args()
    
    # Create and run system
    system = SupplierChurnSystem()
    generate = args.generate_data or (not os.path.exists('transactions.csv'))
    success = system.run_full_pipeline(generate_data=generate)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
