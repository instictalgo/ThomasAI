import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Add the parent directory to sys.path to allow importing our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.payment_tracker import Payment
from models.budget_tracker import Project, Expense
from database.db_manager import engine, SessionLocal

def initialize_projects():
    """Initialize project data and associate payments with projects"""
    print("Initializing project data...")
    
    # Create tables if they don't exist
    from models.budget_tracker import Base
    Base.metadata.create_all(engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Define our projects
        projects = [
            {
                "name": "Piece Quest",
                "total_budget": 20000.00,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            },
            {
                "name": "Tower Defense War",
                "total_budget": 20000.00,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            },
            {
                "name": "Superhero Tower Defense",
                "total_budget": 20000.00,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            },
            {
                "name": "Anime Stars",
                "total_budget": 20000.00,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            },
            {
                "name": "Jujutsu Adventures",
                "total_budget": 20000.00,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            }
        ]
        
        # Create projects if they don't exist
        project_mapping = {}  # Map project names to project objects
        for project_data in projects:
            existing_project = db.query(Project).filter(Project.name == project_data["name"]).first()
            
            if not existing_project:
                # Create new project
                new_project = Project(
                    name=project_data["name"],
                    total_budget=project_data["total_budget"],
                    start_date=project_data["start_date"],
                    end_date=project_data["end_date"]
                )
                db.add(new_project)
                db.flush()  # Flush to get the ID
                project_mapping[project_data["name"]] = new_project
                print(f"Created project: {project_data['name']}")
            else:
                project_mapping[project_data["name"]] = existing_project
                print(f"Project already exists: {project_data['name']}")
        
        # Commit to save projects
        db.commit()
        
        # Now associate payments with projects and create expense records
        print("Associating payments with projects and creating expense records...")
        
        # Get all payments
        payments = db.query(Payment).all()
        
        # Create a mapping of game names to project IDs
        # Note: Some game names in the CSV might have different capitalization or formatting
        game_to_project = {
            "Piece Quest": project_mapping["Piece Quest"].id,
            "Tower Defense War": project_mapping["Tower Defense War"].id,
            "Superhero Tower Defense": project_mapping["Superhero Tower Defense"].id,
            "Anime Stars": project_mapping["Anime Stars"].id,
            "Jujutsu Adventures": project_mapping["Jujutsu Adventures"].id,
            # Add variations if needed
            "4B": None  # This appears in the CSV but isn't one of our main projects
        }
        
        # Load CSV to get game information for each payment
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "payments.csv")
        payment_df = pd.read_csv(csv_path)
        
        # Create a mapping of employee+date to game
        emp_date_to_game = {}
        for _, row in payment_df.iterrows():
            date_str = pd.to_datetime(row['Date'], format='%m/%d/%Y').strftime('%Y%m%d')
            key = f"{row['Employee Name']}_{date_str}"
            emp_date_to_game[key] = row['Game']
        
        # Process payments and create expenses
        expenses_added = 0
        for payment in payments:
            # Extract date in format YYYYMMDD
            if payment.created_at:
                date_str = payment.created_at.strftime('%Y%m%d')
                key = f"{payment.employee_id}_{date_str}"
                
                # Look up which game this payment is for
                game = emp_date_to_game.get(key)
                
                if game and game in game_to_project and game_to_project[game]:
                    project_id = game_to_project[game]
                    
                    # Check if expense already exists
                    existing_expense = db.query(Expense).filter(
                        Expense.project_id == project_id,
                        Expense.description == f"Payment to {payment.employee_id}",
                        Expense.date == payment.created_at.strftime('%Y-%m-%d')
                    ).first()
                    
                    if not existing_expense:
                        # Create expense record
                        expense = Expense(
                            project_id=project_id,
                            category="Development",  # Default category
                            amount=payment.amount * 150 if payment.currency == "SOL" else payment.amount,  # Convert SOL to USD at $150/SOL
                            date=payment.created_at.strftime('%Y-%m-%d'),
                            description=f"Payment to {payment.employee_id}"
                        )
                        db.add(expense)
                        expenses_added += 1
        
        # Commit to save expenses
        db.commit()
        print(f"Added {expenses_added} expense records based on payments.")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing projects: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    initialize_projects() 