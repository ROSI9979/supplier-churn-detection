"""
Real-Time Alert System
Sends email notifications for high-risk customers
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json


class AlertSystem:
    """Handles sending alerts for at-risk customers"""
    
    def __init__(self, email_from=None, email_password=None):
        """
        Initialize alert system
        
        Args:
            email_from: Sender email address (Gmail recommended)
            email_password: Email password or app password
        """
        self.email_from = email_from
        self.email_password = email_password
    
    def format_currency(self, value):
        """Format currency as £X,XXX"""
        return f"£{value:,.0f}"
    
    def create_alert_email_body(self, high_risk_customers):
        """Create HTML email body for alert"""
        
        # Sort by CLV (highest value at risk first)
        sorted_customers = sorted(
            high_risk_customers,
            key=lambda x: x.get('clv', 0),
            reverse=True
        )[:5]  # Top 5 customers
        
        # Calculate totals
        total_at_risk = sum([c.get('clv', 0) for c in high_risk_customers])
        total_discount_cost = sum([c.get('discount_cost', 0) for c in high_risk_customers])
        
        # HTML Email Template
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; }}
                .header {{ background-color: #d32f2f; color: white; padding: 15px; text-align: center; }}
                .customer {{ border-left: 4px solid #d32f2f; padding: 15px; margin: 10px 0; background-color: #fafafa; }}
                .metric {{ display: inline-block; margin-right: 20px; }}
                .metric-label {{ color: #666; font-size: 12px; }}
                .metric-value {{ font-size: 18px; font-weight: bold; color: #d32f2f; }}
                .summary {{ background-color: #fff3e0; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .action {{ background-color: #e8f5e9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .footer {{ color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 CHURN ALERT - IMMEDIATE ACTION REQUIRED</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>
                
                <h2>⏰ {len(high_risk_customers)} High-Risk Customers Detected</h2>
                <p>Below are the customers at highest risk of churning, prioritized by revenue impact:</p>
                
                <div class="summary">
                    <h3>📊 SUMMARY</h3>
                    <div class="metric">
                        <div class="metric-label">Customers at Risk</div>
                        <div class="metric-value">{len(high_risk_customers)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Revenue at Risk</div>
                        <div class="metric-value">{self.format_currency(total_at_risk)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Investment to Save</div>
                        <div class="metric-value">{self.format_currency(total_discount_cost)}</div>
                    </div>
                </div>
                
                <h3>🔴 TOP AT-RISK CUSTOMERS</h3>
        """
        
        # Add each customer
        for idx, customer in enumerate(sorted_customers, 1):
            days_until = customer.get('days_until_churn', '?')
            churn_date = customer.get('predicted_churn_date', 'Unknown')
            clv = self.format_currency(customer.get('clv', 0))
            risk_score = customer.get('churn_risk_score', 0)
            discount = customer.get('recommended_discount_pct', 0)
            action = customer.get('action', 'Monitor')
            priority = customer.get('priority', 'Medium')
            
            html_body += f"""
                <div class="customer">
                    <h4>{idx}. {customer['customer_id']} - Priority: <strong>{priority}</strong></h4>
                    
                    <div class="metric">
                        <div class="metric-label">⏰ Churn In</div>
                        <div class="metric-value">{days_until} days</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">📅 By</div>
                        <div class="metric-value">{churn_date}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">💰 Value at Risk</div>
                        <div class="metric-value">{clv}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">🎯 Risk Score</div>
                        <div class="metric-value">{risk_score:.0f}/100</div>
                    </div>
                    
                    <p><strong>Recommended Action:</strong></p>
                    <div class="action">
                        {action}
                        <br><strong>Offer Discount:</strong> {discount}%
                    </div>
                </div>
            """
        
        # Footer with recommendations
        html_body += f"""
                <h3>✅ RECOMMENDED ACTIONS (By Priority)</h3>
                <ol>
        """
        
        for idx, customer in enumerate(sorted_customers, 1):
            html_body += f"""
                    <li><strong>{customer['customer_id']}</strong> - {customer.get('action', 'Monitor')} 
                        (Save {self.format_currency(customer.get('clv', 0))})</li>
            """
        
        html_body += """
                </ol>
                
                <div class="footer">
                    <p>This is an automated alert from the Supplier Churn Detection System.</p>
                    <p>Log in to the dashboard for full details: 
                    <a href="https://share.streamlit.io/ROSI9979/supplier-churn-detection">
                    Churn Detection Dashboard</a></p>
                    <p>Alert sent: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def create_alert_text_body(self, high_risk_customers):
        """Create plain text email body for alert"""
        
        sorted_customers = sorted(
            high_risk_customers,
            key=lambda x: x.get('clv', 0),
            reverse=True
        )[:5]
        
        total_at_risk = sum([c.get('clv', 0) for c in high_risk_customers])
        
        text_body = f"""
CHURN ALERT - IMMEDIATE ACTION REQUIRED
{datetime.now().strftime('%A, %B %d, %Y')}

SUMMARY
=======
Customers at Risk: {len(high_risk_customers)}
Total Revenue at Risk: {self.format_currency(total_at_risk)}

TOP AT-RISK CUSTOMERS (by revenue impact)
==========================================
"""
        
        for idx, customer in enumerate(sorted_customers, 1):
            days_until = customer.get('days_until_churn', '?')
            churn_date = customer.get('predicted_churn_date', 'Unknown')
            clv = self.format_currency(customer.get('clv', 0))
            risk_score = customer.get('churn_risk_score', 0)
            discount = customer.get('recommended_discount_pct', 0)
            action = customer.get('action', 'Monitor')
            priority = customer.get('priority', 'Medium')
            
            text_body += f"""
{idx}. {customer['customer_id']} - Priority: {priority}
   ⏰ Churn in: {days_until} days (by {churn_date})
   💰 Value at Risk: {clv}
   🎯 Risk Score: {risk_score:.0f}/100
   📌 Action: {action}
   💯 Discount: {discount}%
"""
        
        text_body += """

RECOMMENDED ACTIONS
===================
Contact the above customers in priority order.
Offer the recommended discounts to retain them.

View full dashboard: https://share.streamlit.io/ROSI9979/supplier-churn-detection

---
This is an automated alert from Supplier Churn Detection System
"""
        
        return text_body
    
    def send_email_alert(self, recipient_email, high_risk_customers, use_gmail=False):
        """
        Send email alert for high-risk customers
        
        Args:
            recipient_email: Email address to send to
            high_risk_customers: List of high-risk customer data
            use_gmail: True for Gmail SMTP, False for console printing (testing)
        """
        
        if not high_risk_customers:
            print("✓ No high-risk customers to alert")
            return True
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 URGENT: {len(high_risk_customers)} Customers at Risk"
        msg['From'] = self.email_from or "churn-alerts@system.local"
        msg['To'] = recipient_email
        
        # Create email body
        text_body = self.create_alert_text_body(high_risk_customers)
        html_body = self.create_alert_email_body(high_risk_customers)
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        if use_gmail and self.email_from and self.email_password:
            try:
                # Send via Gmail
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
                server.quit()
                
                print(f"✓ Email alert sent to {recipient_email}")
                return True
            except Exception as e:
                print(f"✗ Failed to send email: {e}")
                return False
        else:
            # Just print to console (for testing without email setup)
            print(f"\n{'='*80}")
            print(f"EMAIL ALERT (Would be sent to: {recipient_email})")
            print(f"{'='*80}")
            print(f"Subject: {msg['Subject']}")
            print(f"{'='*80}")
            print(text_body)
            print(f"{'='*80}\n")
            return True
    
    def print_alert_summary(self, high_risk_customers):
        """Print alert summary to console"""
        
        if not high_risk_customers:
            print("✓ No high-risk customers")
            return
        
        sorted_customers = sorted(
            high_risk_customers,
            key=lambda x: x.get('clv', 0),
            reverse=True
        )
        
        total_at_risk = sum([c.get('clv', 0) for c in high_risk_customers])
        
        print("\n" + "="*80)
        print("🚨 CHURN ALERTS")
        print("="*80)
        print(f"\n{len(high_risk_customers)} High-Risk Customers Detected")
        print(f"Total Revenue at Risk: {self.format_currency(total_at_risk)}\n")
        
        print("Top Customers (by revenue impact):")
        print("-"*80)
        
        for idx, customer in enumerate(sorted_customers[:5], 1):
            days = customer.get('days_until_churn', '?')
            clv = self.format_currency(customer.get('clv', 0))
            risk = customer.get('churn_risk_score', 0)
            priority = customer.get('priority', 'Medium')
            
            print(f"{idx}. {customer['customer_id']}")
            print(f"   Priority: {priority} | Risk: {risk:.0f}/100 | Churn in {days} days | Value: {clv}")
