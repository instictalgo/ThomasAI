import csv
import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Add the parent directory to sys.path to allow importing our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.payment_tracker import Payment
from database.db_manager import engine, SessionLocal
from models.base import Base

def import_payments_from_csv(csv_path):
    """Import payments from CSV file into the database"""
    print(f"Importing payments from {csv_path}...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Read CSV with pandas to handle potential formatting issues
        df = pd.read_csv(csv_path)
        
        # Convert Date column to proper format
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        
        # Process each row
        payments_added = 0
        for _, row in df.iterrows():
            try:
                # Determine amount and currency
                if pd.notna(row['Crypto Amount (SOL)']) and row['Crypto Amount (SOL)'] != '-':
                    amount = float(row['Crypto Amount (SOL)'])
                    currency = "SOL"
                    payment_method = "crypto_sol"
                elif pd.notna(row['USD Paid']) and row['USD Paid'] != '-':
                    # Remove $ and convert to float
                    amount = float(str(row['USD Paid']).replace('$', '').replace(',', ''))
                    currency = "USD"
                    payment_method = "bank" if row['Method'] == "Bank" else "paypal"
                else:
                    print(f"Skipping row for {row['Employee Name']} - no valid payment amount")
                    continue  # Skip if no amount info or if it's "-"
                
                # Create payment record
                payment = Payment(
                    employee_id=row['Employee Name'],
                    amount=amount,
                    currency=currency,
                    payment_method=payment_method,
                    status="completed" if row['Status'] == "Paid" else "pending",
                    transaction_id=f"imported_{row['Employee Name']}_{row['Date'].strftime('%Y%m%d')}",
                    created_at=row['Date'].to_pydatetime(),
                    completed_at=row['Date'].to_pydatetime() if row['Status'] == "Paid" else None
                )
                
                # Add to database
                db.add(payment)
                payments_added += 1
            except Exception as e:
                print(f"Error processing row for {row['Employee Name']}: {str(e)}")
                continue
            
        # Commit changes
        db.commit()
        print(f"Successfully imported {payments_added} payment records.")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing payments: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "payments.csv")
    import_payments_from_csv(csv_path)
