#!/usr/bin/env python3
import sys
import os

# Print debug info
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Path: {sys.path}")

# Try imports one by one
try:
    print("Importing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except Exception as e:
    print(f"❌ FastAPI import error: {e}")

try:
    print("Importing SQLAlchemy...")
    from sqlalchemy import create_engine
    print("✅ SQLAlchemy imported successfully")
except Exception as e:
    print(f"❌ SQLAlchemy import error: {e}")

# Try importing our own modules
try:
    print("Adding parent directory to path...")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    print(f"Updated path: {sys.path}")
    
    print("Importing models.payment_tracker...")
    from models.payment_tracker import Payment
    print("✅ models.payment_tracker imported successfully")
except Exception as e:
    print(f"❌ models.payment_tracker import error: {e}")

try:
    print("Importing models.base...")
    from models.base import Base
    print("✅ models.base imported successfully")
except Exception as e:
    print(f"❌ models.base import error: {e}")

try:
    print("Importing database.db_manager...")
    from database.db_manager import engine, SessionLocal
    print("✅ database.db_manager imported successfully")
except Exception as e:
    print(f"❌ database.db_manager import error: {e}")

print("Import checks complete")
