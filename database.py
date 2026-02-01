import sqlite3
import pandas as pd
from datetime import datetime
import os

class SupplierDatabase:
    """SQLite database for storing transactions and churn predictions"""
    
    def __init__(self, db_name='supplier_churn.db'):
        self.db_name = db_name
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                product TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_value REAL NOT NULL,
                month INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Customer metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                avg_spending REAL,
                spending_trend REAL,
                spending_volatility REAL,
                recent_vs_historical_pct REAL,
                zero_spending_months INTEGER,
                total_months INTEGER,
                churn_risk_score REAL,
                risk_level TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Churn predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS churn_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                products_at_risk TEXT,
                recommended_discount_pct INTEGER,
                action TEXT,
                priority TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Retention actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retention_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                action_type TEXT,
                discount_offered REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✓ Database initialized successfully")
    
    def insert_transactions(self, df):
        """Insert transaction data into database"""
        df.to_sql('transactions', self.conn, if_exists='append', index=False)
        self.conn.commit()
        print(f"✓ Inserted {len(df)} transactions into database")
    
    def insert_metrics(self, metrics_df):
        """Insert customer metrics"""
        # Remove timestamp columns for insert
        insert_df = metrics_df[['customer_id', 'avg_spending', 'spending_trend', 
                                'spending_volatility', 'recent_vs_historical_pct',
                                'zero_spending_months', 'total_months', 
                                'churn_risk_score', 'risk_level']].copy()
        
        for _, row in insert_df.iterrows():
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO customer_metrics 
                (customer_id, avg_spending, spending_trend, spending_volatility,
                 recent_vs_historical_pct, zero_spending_months, total_months,
                 churn_risk_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(row))
        
        self.conn.commit()
        print(f"✓ Updated {len(insert_df)} customer metrics")
    
    def insert_predictions(self, strategies_df):
        """Insert churn predictions"""
        for _, row in strategies_df.iterrows():
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO churn_predictions 
                (customer_id, products_at_risk, recommended_discount_pct, action, priority)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['customer_id'], row['products_at_risk'], 
                  row['recommended_discount_pct'], row['action'], row['priority']))
        
        self.conn.commit()
        print(f"✓ Inserted {len(strategies_df)} churn predictions")
    
    def get_high_risk_customers(self):
        """Retrieve high-risk customers"""
        query = '''
            SELECT customer_id, churn_risk_score, risk_level, spending_trend,
                   recent_vs_historical_pct
            FROM customer_metrics
            WHERE risk_level = 'High Risk'
            ORDER BY churn_risk_score DESC
        '''
        return pd.read_sql_query(query, self.conn)
    
    def get_customer_history(self, customer_id):
        """Get transaction history for a specific customer"""
        query = '''
            SELECT date, product, quantity, unit_price, total_value
            FROM transactions
            WHERE customer_id = ?
            ORDER BY date ASC
        '''
        return pd.read_sql_query(query, self.conn, params=(customer_id,))
    
    def get_retention_recommendations(self):
        """Get all pending retention actions"""
        query = '''
            SELECT customer_id, products_at_risk, recommended_discount_pct, action, priority
            FROM churn_predictions
            ORDER BY priority DESC, customer_id
        '''
        return pd.read_sql_query(query, self.conn)
    
    def log_retention_action(self, customer_id, discount_offered):
        """Log a retention action taken"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO retention_actions (customer_id, action_type, discount_offered)
            VALUES (?, ?, ?)
        ''', (customer_id, 'discount_offer', discount_offered))
        
        self.conn.commit()
    
    def get_action_history(self):
        """Get history of all retention actions"""
        query = '''
            SELECT customer_id, action_type, discount_offered, status, created_at
            FROM retention_actions
            ORDER BY created_at DESC
        '''
        return pd.read_sql_query(query, self.conn)
    
    def get_dashboard_summary(self):
        """Get summary statistics for dashboard"""
        summary = {
            'total_customers': self.conn.execute(
                'SELECT COUNT(DISTINCT customer_id) FROM customer_metrics'
            ).fetchone()[0],
            'high_risk_customers': self.conn.execute(
                "SELECT COUNT(*) FROM customer_metrics WHERE risk_level = 'High Risk'"
            ).fetchone()[0],
            'medium_risk_customers': self.conn.execute(
                "SELECT COUNT(*) FROM customer_metrics WHERE risk_level = 'Medium Risk'"
            ).fetchone()[0],
            'avg_churn_score': round(self.conn.execute(
                'SELECT AVG(churn_risk_score) FROM customer_metrics'
            ).fetchone()[0], 2),
            'total_transactions': self.conn.execute(
                'SELECT COUNT(*) FROM transactions'
            ).fetchone()[0],
            'actions_pending': self.conn.execute(
                "SELECT COUNT(*) FROM retention_actions WHERE status = 'pending'"
            ).fetchone()[0]
        }
        return summary
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    db = SupplierDatabase()
    summary = db.get_dashboard_summary()
    print("\nDatabase Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    db.close()
