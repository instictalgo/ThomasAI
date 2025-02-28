from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database.db_manager import get_db
from models.budget_tracker import Project, Expense
from models.payment_tracker import Payment
from models.asset_tracker import Asset
import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get details for a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()

@router.get("/{project_id}/expenses")
def get_project_expenses(project_id: int, db: Session = Depends(get_db)):
    """Get all expenses for a specific project"""
    expenses = db.query(Expense).filter(Expense.project_id == project_id).all()
    return [expense.to_dict() for expense in expenses]

@router.get("/{project_id}/team")
def get_project_team(project_id: int, db: Session = Depends(get_db)):
    """Get team members who worked on a specific project"""
    # This is a placeholder implementation as we don't have a direct project-team relationship
    # In a real system, we'd have a more direct way to get this data
    
    # Get all payments that are for this project
    # This is just an example - real implementation would depend on your data model
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # For now, return a list of all employees with some mock data
    employees = db.query(Payment.employee_id).distinct().all()
    team = []
    for emp in employees:
        emp_id = emp[0]
        payments = db.query(Payment).filter(Payment.employee_id == emp_id).all()
        total_paid = sum(p.amount for p in payments if p.currency == "USD")
        
        team.append({
            "name": emp_id,
            "role": "Developer",  # Mock data
            "tasks": "Various development tasks",  # Mock data
            "amount_paid": total_paid
        })
    
    return team

@router.get("/{project_id}/assets")
def get_project_assets(project_id: int, db: Session = Depends(get_db)):
    """Get all assets for a specific project"""
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    return [asset.to_dict() for asset in assets]

@router.get("/{project_id}/budget")
def get_project_budget(project_id: int, db: Session = Depends(get_db)):
    """Get budget information for a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    expenses = db.query(Expense).filter(Expense.project_id == project_id).all()
    
    # Calculate totals
    total_spent = sum(expense.amount for expense in expenses)
    remaining = project.total_budget - total_spent
    
    # Group by category
    categories = {}
    for expense in expenses:
        if expense.category not in categories:
            categories[expense.category] = 0
        categories[expense.category] += expense.amount
    
    return {
        "total_budget": project.total_budget,
        "total_spent": total_spent,
        "remaining": remaining,
        "categories": categories
    }

@router.get("/{project_id}/progress")
def get_project_progress(project_id: int, db: Session = Depends(get_db)):
    """Get progress information for a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    
    # Calculate progress metrics
    if assets:
        overall_progress = sum(asset.progress for asset in assets) / len(assets)
        complete_assets = sum(1 for asset in assets if asset.progress == 100)
        in_progress_assets = sum(1 for asset in assets if 0 < asset.progress < 100)
        not_started_assets = sum(1 for asset in assets if asset.progress == 0)
        
        # Progress by type
        progress_by_type = {}
        for asset in assets:
            asset_type = asset.asset_type
            if asset_type not in progress_by_type:
                progress_by_type[asset_type] = {"total": 0, "count": 0}
            progress_by_type[asset_type]["total"] += asset.progress
            progress_by_type[asset_type]["count"] += 1
        
        for asset_type in progress_by_type:
            progress_by_type[asset_type]["average"] = (
                progress_by_type[asset_type]["total"] / progress_by_type[asset_type]["count"]
            )
    else:
        overall_progress = 0
        complete_assets = 0
        in_progress_assets = 0
        not_started_assets = 0
        progress_by_type = {}
    
    return {
        "overall_progress": overall_progress,
        "asset_count": len(assets),
        "complete_assets": complete_assets,
        "in_progress_assets": in_progress_assets,
        "not_started_assets": not_started_assets,
        "progress_by_type": progress_by_type
    }
