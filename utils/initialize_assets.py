import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import random

# Add the parent directory to sys.path to allow importing our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.asset_tracker import Asset, AssetType, AssetStatus
from models.budget_tracker import Project
from database.db_manager import engine, SessionLocal
from models.base import Base

def initialize_assets():
    """Initialize asset data based on the roles in the payments CSV"""
    print("Initializing asset data...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Get all projects
        projects = db.query(Project).all()
        project_mapping = {project.name: project.id for project in projects}
        
        # Load CSV to get roles
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "payments.csv")
        payment_df = pd.read_csv(csv_path)
        
        # Extract unique roles and games
        roles = payment_df['Role'].unique()
        
        # Create asset records for each role and project
        assets_added = 0
        
        # Map roles to asset types (as strings)
        role_to_asset_type = {
            "Modeler": "model_3d",
            "Animator": "animation",
            "Programmer": "script",
            "VFX": "animation",
            "Builder": "model_3d",
            "UI Artist": "ui",
            "Thumbnail Artist": "ui",
            "VFX + Programmer": "script",
            # Default for other roles
            "DEFAULT": "model_3d"
        }
        
        # Create typical asset names for each role
        role_to_asset_names = {
            "Modeler": ["Character Models", "Environment Models", "Prop Models", "Weapon Models"],
            "Animator": ["Character Animations", "Attack Animations", "Idle Animations", "Special Move Animations"],
            "Programmer": ["Core Gameplay Logic", "Combat System", "Inventory System", "Quest System", "Economy System"],
            "VFX": ["Particle Effects", "Spell Effects", "Combat Effects", "Environment Effects"],
            "Builder": ["Main Map", "Hub Area", "Dungeons", "Battle Arenas"],
            "UI Artist": ["Main Menu UI", "HUD Design", "Inventory UI", "Shop UI"],
            "Thumbnail Artist": ["Game Thumbnails", "Update Thumbnails", "Promotional Art"],
            "VFX + Programmer": ["Special Effect Systems", "Visual Scripting Systems"],
            # Default
            "DEFAULT": ["General Asset"]
        }
        
        # Status options as strings
        status_options = ["not_started", "in_progress", "review", "complete"]
        
        # For each project and role, create assets
        for project_name, project_id in project_mapping.items():
            # Filter roles that exist for this project
            project_roles = payment_df[payment_df['Game'] == project_name]['Role'].dropna().unique()
            
            if len(project_roles) == 0:
                # Use all roles if none specifically match
                project_roles = roles
            
            for role in project_roles:
                # Get asset type for this role
                asset_type = role_to_asset_type.get(role, role_to_asset_type["DEFAULT"])
                
                # Get possible asset names for this role
                asset_names = role_to_asset_names.get(role, role_to_asset_names["DEFAULT"])
                
                # Get employees with this role
                employees = payment_df[payment_df['Role'] == role]['Employee Name'].dropna().unique()
                if len(employees) == 0:
                    employees = ["Unassigned"]
                
                # Create 1-3 assets for this role and project
                for asset_name in random.sample(asset_names, min(3, len(asset_names))):
                    # Check if asset already exists
                    existing_asset = db.query(Asset).filter(
                        Asset.name == f"{project_name} - {asset_name}",
                        Asset.project_id == project_id
                    ).first()
                    
                    if not existing_asset:
                        # Create new asset with random progress
                        new_asset = Asset(
                            name=f"{project_name} - {asset_name}",
                            description=f"{asset_name} for {project_name}",
                            asset_type=asset_type,  # Store as string, not enum
                            status=random.choice(status_options),  # Store as string, not enum
                            progress=random.randint(0, 100),
                            assigned_to=random.choice(employees),
                            project_id=project_id,
                            created_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                            due_date=(datetime.datetime.now() + datetime.timedelta(days=random.randint(7, 60))).strftime("%Y-%m-%d")
                        )
                        db.add(new_asset)
                        assets_added += 1
        
        # Commit to save assets
        db.commit()
        print(f"Added {assets_added} asset records.")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing assets: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    initialize_assets()
