import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def import_data():
    print("Starting data import...")
    
    try:
        # First initialize the database
        from init_db import init_db
        init_db()
        
        # Check if the payments.csv file exists
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "payments.csv")
        if not os.path.exists(csv_path):
            print(f"ERROR: The payments.csv file does not exist at {csv_path}")
            return False
        
        # Import payments
        from utils.import_payments import import_payments_from_csv
        import_payments_from_csv(csv_path)
        
        # Initialize projects
        from utils.initialize_projects import initialize_projects
        initialize_projects()
        
        # Initialize assets
        from utils.initialize_assets import initialize_assets
        initialize_assets()
        
        print("Data import completed successfully.")
        return True
    except Exception as e:
        print(f"ERROR during data import: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import_data()
