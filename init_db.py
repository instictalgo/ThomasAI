import os
import sys
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db_initializer')

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the database engine
from database.db_manager import engine

# Import all models to ensure they're registered with the Base
from models.base import Base
from models.payment_tracker import Payment
from models.budget_tracker import Project, Expense
from models.asset_tracker import Asset, asset_dependency

def check_sqlite_connection(db_path):
    """Verify SQLite database connection and file integrity"""
    logger.info(f"Checking SQLite database at {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == 'ok':
            logger.info("SQLite database integrity check passed")
            return True
        else:
            logger.error(f"SQLite database integrity check failed: {result}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to SQLite database: {str(e)}")
        return False

def init_db():
    """Initialize the database with all tables"""
    logger.info("Creating database tables...")
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        # For SQLite database, verify the file exists and connection works
        if 'sqlite' in str(engine.url):
            db_path = str(engine.url).replace('sqlite:///', '')
            if os.path.exists(db_path):
                if check_sqlite_connection(db_path):
                    logger.info(f"Successfully connected to SQLite database at {db_path}")
                    return True
                else:
                    logger.error(f"Database file exists but connection failed")
                    return False
            else:
                logger.error(f"Database file not found at {db_path}")
                return False
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        print("Database initialized successfully!")
        sys.exit(0)
    else:
        print("Database initialization failed!")
        sys.exit(1)
