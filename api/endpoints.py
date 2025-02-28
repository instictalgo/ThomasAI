from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.payment_tracker import Payment
from models.budget_tracker import Project, Expense
from database.db_manager import get_db

router = APIRouter()

@router.get("/projects/", response_model=List[dict])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [project.to_dict() for project in projects]

@router.get("/payments/employees", response_model=List[str])
def get_all_employees(db: Session = Depends(get_db)):
    """Get a list of all employees who have received payments"""
    employees = db.query(Payment.employee_id).distinct().all()
    return [emp[0] for emp in employees]

@router.get("/payments/employee/{employee_id}", response_model=List[dict])
def get_employee_payments(employee_id: str, db: Session = Depends(get_db)):
    """Get all payments for a specific employee"""
    payments = db.query(Payment).filter(Payment.employee_id == employee_id).all()
    return [payment.to_dict() for payment in payments]
