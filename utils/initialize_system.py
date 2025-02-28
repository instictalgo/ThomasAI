import os
import sys
import time

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import initialization functions
from utils.import_payments import import_payments_from_csv
from utils.initialize_projects import initialize_projects
from utils.initialize_assets import initialize_assets

def initialize_system():
    """Initialize the entire Thomas AI system database"""
    print("Starting Thomas AI system initialization...")
    
    # Step 1: Import payments from CSV
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "payments.csv")
    import_payments_from_csv(csv_path)
    time.sleep(1)  # Short pause for better console output readability
    
    # Step 2: Initialize projects and associate payments
    initialize_projects()
    time.sleep(1)
    
    # Step 3: Initialize assets based on roles
    initialize_assets()
    
    print("\nThomas AI system initialization complete!")
    print("\nNext steps:")
    print("1. Start the system with 'python thomas_app/run.py'")
    print("2. Access the dashboard at http://localhost:8501")
    print("3. Chat with Thomas AI at http://localhost:8501/chat_with_thomas")

if __name__ == "__main__":
    initialize_system() 