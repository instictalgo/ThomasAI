from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

# Import the shared Base
from models.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    total_budget = Column(Float)
    start_date = Column(String)
    end_date = Column(String)
    
    # Relationships - don't refer to Asset directly to avoid circular imports
    expenses = relationship("Expense", back_populates="project")
    
    def to_dict(self):
        """Convert project object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "total_budget": self.total_budget,
            "start_date": self.start_date,
            "end_date": self.end_date
        }

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    category = Column(String)
    amount = Column(Float)
    date = Column(String)
    description = Column(String)
    
    # Relationships
    project = relationship("Project", back_populates="expenses")
    
    def to_dict(self):
        """Convert expense object to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "category": self.category,
            "amount": self.amount,
            "date": self.date,
            "description": self.description
        }
