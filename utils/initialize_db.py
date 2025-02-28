import os
import sys
import sqlite3

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_database():
    """Create the SQLite database file if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "thomas_ai.db")
    
    print(f"Creating database at: {db_path}")
    
    # If the file doesn't exist, create it
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
        print("Database file created successfully")
    else:
        print("Database file already exists")
    
    return db_path

if __name__ == "__main__":
    create_database() 