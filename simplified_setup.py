import os
import sys
import sqlite3
import importlib.util
import time

def create_database():
    """Create the SQLite database file if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thomas_ai.db")
    
    print(f"Creating database at: {db_path}")
    
    # If the file doesn't exist, create it
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
        print("Database file created successfully")
    else:
        print("Database file already exists")
    
    return db_path

def main():
    """Main setup function"""
    print("\n===== Thomas AI System Setup =====\n")
    
    # Create database file
    create_database()
    
    print("\nSetup completed. You can now run the following commands:")
    print("1. cd ~/thomas_app")
    print("2. python3 utils/initialize_system.py")
    print("3. python3 run.py")

if __name__ == "__main__":
    main()
