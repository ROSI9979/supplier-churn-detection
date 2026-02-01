import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class TransactionDataGenerator:
    """Generate realistic B2B supplier transaction data with churn patterns"""
    
    def __init__(self, num_customers=50, months=12, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        self.num_customers = num_customers
        self.months = months
        self.products = ['Chicken Dips', 'Cheese Dips', 'Drinks', 'Sauces', 'Frozen Items']
        self.customers = [f'Customer_{i:03d}' for i in range(num_customers)]
    
    def generate_baseline_purchases(self):
        """Create baseline purchasing patterns for each customer"""
        baseline = {}
        for customer in self.customers:
            baseline[customer] = {
                product: np.random.randint(5, 50) 
                for product in self.products
            }
        return baseline
    
    def generate_transactions(self):
        """Generate 12 months of transaction data with churn patterns"""
        transactions = []
        baseline = self.generate_baseline_purchases()
        
        # Mark some customers as "churned" (will reduce purchases)
        churned_customers = random.sample(self.customers, k=int(0.3 * self.num_customers))
        churn_start_month = random.randint(6, 10)  # Churn happens mid-year
        
        start_date = datetime(2023, 1, 1)
        
        for month in range(self.months):
            current_date = start_date + timedelta(days=30*month)
            
            for customer in self.customers:
                for product in self.products:
                    base_qty = baseline[customer][product]
                    
                    # Add natural variation
                    qty = base_qty + np.random.randint(-5, 5)
                    
                    # If customer has churned, gradually reduce purchases
                    if customer in churned_customers and month >= churn_start_month:
                        churn_progress = (month - churn_start_month) / (self.months - churn_start_month)
                        reduction_factor = 1 - (churn_progress * np.random.uniform(0.3, 0.8))
                        qty = int(qty * reduction_factor)
                    
                    qty = max(0, qty)  # Ensure non-negative
                    price = np.random.uniform(5, 50)  # Random pricing
                    
                    transactions.append({
                        'date': current_date,
                        'customer_id': customer,
                        'product': product,
                        'quantity': qty,
                        'unit_price': round(price, 2),
                        'total_value': round(qty * price, 2),
                        'month': month + 1
                    })
        
        return pd.DataFrame(transactions)
    
    def save_data(self, filename='transactions.csv'):
        """Generate and save transaction data"""
        df = self.generate_transactions()
        df.to_csv(filename, index=False)
        print(f"✓ Generated {len(df)} transactions and saved to {filename}")
        return df


if __name__ == "__main__":
    generator = TransactionDataGenerator(num_customers=50, months=12)
    df = generator.save_data('transactions.csv')
    print(f"\nDataset shape: {df.shape}")
    print("\nFirst few records:")
    print(df.head(10))
