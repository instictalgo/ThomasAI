#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL.
This script helps migrate the knowledge base data from the SQLite database
to a new PostgreSQL database.

Usage:
    python migrate_to_postgresql.py --sqlite-path path/to/sqlite.db --pg-connection postgresql://user:pass@host:port/dbname

Requirements:
    - sqlalchemy
    - psycopg2-binary
    - python-dotenv
"""

import os
import sys
import argparse
import logging
import time
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("migration")

def parse_args():
    parser = argparse.ArgumentParser(description="Migrate data from SQLite to PostgreSQL")
    parser.add_argument(
        "--sqlite-path", 
        dest="sqlite_path",
        help="Path to SQLite database file",
        default=os.getenv("SQLITE_PATH", "./thomas_ai.db")
    )
    parser.add_argument(
        "--pg-connection",
        dest="pg_connection",
        help="PostgreSQL connection string (postgresql://user:pass@host:port/dbname)",
        default=os.getenv("PG_CONNECTION")
    )
    parser.add_argument(
        "--tables",
        dest="tables",
        help="Comma-separated list of tables to migrate (default: all)",
        default=None
    )
    parser.add_argument(
        "--drop-existing",
        dest="drop_existing",
        help="Drop existing tables in PostgreSQL before migration",
        action="store_true",
        default=False
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.sqlite_path:
        parser.error("SQLite path is required. Use --sqlite-path or set SQLITE_PATH environment variable.")
    
    if not args.pg_connection:
        parser.error("PostgreSQL connection string is required. Use --pg-connection or set PG_CONNECTION environment variable.")
    
    return args

def get_sqlite_engine(sqlite_path):
    """Get SQLAlchemy engine for SQLite database."""
    return create_engine(f"sqlite:///{sqlite_path}")

def get_pg_engine(pg_connection):
    """Get SQLAlchemy engine for PostgreSQL database."""
    return create_engine(pg_connection)

def get_all_tables(engine):
    """Get all tables from a database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def copy_table_structure(source_engine, dest_engine, table_name, drop_existing=False):
    """Copy table structure from source to destination."""
    source_meta = MetaData()
    source_meta.reflect(bind=source_engine, only=[table_name])
    source_table = source_meta.tables[table_name]
    
    dest_meta = MetaData()
    
    # Create a new table with the same structure
    dest_table = Table(
        table_name,
        dest_meta,
        *[Column(c.name, c.type, primary_key=c.primary_key) for c in source_table.columns]
    )
    
    # Drop existing table if requested
    if drop_existing:
        dest_table.drop(dest_engine, checkfirst=True)
    
    # Create the table in the destination database
    dest_table.create(dest_engine, checkfirst=True)
    
    return source_table, dest_table

def copy_table_data(source_engine, dest_engine, table_name, batch_size=1000):
    """Copy data from source table to destination table."""
    # Get table structures
    source_table, dest_table = copy_table_structure(source_engine, dest_engine, table_name)
    
    # Create sessions
    SourceSession = sessionmaker(bind=source_engine)
    source_session = SourceSession()
    
    DestSession = sessionmaker(bind=dest_engine)
    dest_session = DestSession()
    
    # Count total rows
    total_rows = source_session.query(source_table).count()
    logger.info(f"Copying {total_rows} rows from table '{table_name}'")
    
    # Copy data in batches
    offset = 0
    while True:
        # Get a batch of rows
        rows = source_session.query(source_table).offset(offset).limit(batch_size).all()
        if not rows:
            break
        
        # Insert rows into destination
        dest_session.execute(dest_table.insert(), [dict(row) for row in rows])
        dest_session.commit()
        
        # Update offset
        offset += len(rows)
        logger.info(f"Copied {offset}/{total_rows} rows from table '{table_name}'")
    
    source_session.close()
    dest_session.close()
    
    logger.info(f"Successfully copied {offset} rows from table '{table_name}'")
    return offset

def migrate_database(sqlite_path, pg_connection, tables=None, drop_existing=False):
    """Migrate data from SQLite to PostgreSQL."""
    logger.info(f"Starting migration from {sqlite_path} to {pg_connection}")
    
    # Create engines
    sqlite_engine = get_sqlite_engine(sqlite_path)
    pg_engine = get_pg_engine(pg_connection)
    
    # Get all tables if not specified
    if not tables:
        tables = get_all_tables(sqlite_engine)
    else:
        tables = [t.strip() for t in tables.split(",")]
    
    logger.info(f"Tables to migrate: {tables}")
    
    # Migrate each table
    total_rows = 0
    for table_name in tables:
        try:
            rows_copied = copy_table_data(sqlite_engine, pg_engine, table_name, drop_existing=drop_existing)
            total_rows += rows_copied
        except Exception as e:
            logger.error(f"Error migrating table '{table_name}': {str(e)}")
    
    logger.info(f"Migration completed. Total rows copied: {total_rows}")
    return total_rows

def main():
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    # Migrate database
    start_time = time.time()
    try:
        total_rows = migrate_database(
            sqlite_path=args.sqlite_path,
            pg_connection=args.pg_connection,
            tables=args.tables,
            drop_existing=args.drop_existing
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Migration completed successfully in {elapsed_time:.2f} seconds")
        logger.info(f"Total rows migrated: {total_rows}")
        
        return 0
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 