import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import datetime
import argparse

# Fix for numpy compatibility issues with newer versions
try:
    import numpy as np
    # Check if bool8 is missing and add it
    if not hasattr(np, 'bool8'):
        np.bool8 = np.bool_
    # Check if float_ is missing and add it
    if not hasattr(np, 'float_'):
        np.float_ = np.float64
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_server")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our component modules
try:
    from models.payment_tracker import Payment
    from models.budget_tracker import Project, Expense
    from models.asset_tracker import Asset, AssetStatus, AssetType
    from services.trello_manager import TrelloManager
    from services.budget_visualizer import BudgetVisualizer
    from services.payment_processor import PayPalProcessor, CryptoProcessor
    from services.asset_tracker_enhanced import AssetTracker
    from database.db_manager import engine, SessionLocal
    from models.base import Base
    from services.knowledge_base import GameDesignKnowledgeBase
    from services.enhanced_knowledge_base import get_enhanced_knowledge_base
    from models.knowledge_models import TaxonomyNode, GameDesignConcept, IndustryPractice, EducationalResource, MarketResearch
    logger.info("Successfully imported all modules")
except Exception as e:
    logger.error(f"Failed to import modules: {str(e)}")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./thomas_ai.db")
logger.info(f"Using database: {DATABASE_URL}")

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize FastAPI
app = FastAPI(title="Thomas AI Management System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Trello manager
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
trello = TrelloManager(TRELLO_API_KEY, TRELLO_TOKEN)

# Initialize our components
budget_visualizer = BudgetVisualizer()
paypal_processor = PayPalProcessor()
crypto_processor = CryptoProcessor()

# Pydantic models for API
class PaymentCreate(BaseModel):
    employee_id: str
    amount: float
    currency: str = "USD"
    payment_method: str
    
class ProjectCreate(BaseModel):
    name: str
    total_budget: float
    start_date: str
    end_date: str
    
class ExpenseCreate(BaseModel):
    project_id: int
    category: str
    amount: float
    date: str
    description: str
    
class AssetCreate(BaseModel):
    name: str
    description: str
    asset_type: str
    assigned_to: str
    project_id: int
    due_date: str

class TrelloBoardCreate(BaseModel):
    project_name: str
    description: Optional[str] = None
    features: List[dict]
    team_members: List[dict]

# Create API models for knowledge base
class DesignConceptCreate(BaseModel):
    name: str
    description: str
    examples: Optional[str] = None
    references: Optional[str] = None

class IndustryPracticeCreate(BaseModel):
    name: str
    description: str
    companies: Optional[str] = None
    outcomes: Optional[str] = None

class EducationalResourceCreate(BaseModel):
    title: str
    type: str
    url: Optional[str] = None
    description: str
    topics: Optional[str] = None

class MarketResearchCreate(BaseModel):
    title: str
    date: str
    source: Optional[str] = None
    findings: str
    implications: Optional[str] = None

class SearchQuery(BaseModel):
    query: str
    category: Optional[str] = None

# API Routes

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint for the API"""
    return {
        "message": "Thomas AI Management System API is running",
        "documentation": "/docs",
        "version": "1.05"
    }

# Payment routes
@app.post("/payments/", response_model=dict)
def create_payment(payment: PaymentCreate, db=Depends(get_db)):
    db_payment = Payment(
        employee_id=payment.employee_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        status="pending",
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return {"id": db_payment.id, "status": db_payment.status}

@app.get("/payments/", response_model=List[dict])
def list_payments(db=Depends(get_db)):
    payments = db.query(Payment).all()
    return [payment.to_dict() for payment in payments]

@app.get("/payments/employees", response_model=List[str])
def get_all_employees(db=Depends(get_db)):
    """Get a list of all employees who have received payments"""
    employees = db.query(Payment.employee_id).distinct().all()
    return [emp[0] for emp in employees]

@app.get("/payments/employee/{employee_id}", response_model=List[dict])
def get_employee_payments(employee_id: str, db=Depends(get_db)):
    """Get all payments for a specific employee"""
    payments = db.query(Payment).filter(Payment.employee_id == employee_id).all()
    return [payment.to_dict() for payment in payments]

# Project routes
@app.post("/projects/", response_model=dict)
def create_project(project: ProjectCreate, db=Depends(get_db)):
    db_project = Project(
        name=project.name,
        total_budget=project.total_budget,
        start_date=project.start_date,
        end_date=project.end_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"id": db_project.id, "name": db_project.name}

@app.get("/projects/", response_model=List[dict])
def list_projects(db=Depends(get_db)):
    projects = db.query(Project).all()
    return [project.to_dict() for project in projects]

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint to verify API is working"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "database": "disconnected",
            "error": str(e)
        }

# Import project-specific endpoints and include them
from api.project_endpoints import router as project_router
app.include_router(project_router)

# Import enhanced knowledge endpoints
from api.knowledge_endpoints import router as knowledge_router
app.include_router(knowledge_router)

# Schema information endpoint
@app.get("/schema/tables")
def get_schema_info():
    """Get database schema information"""
    try:
        inspector = inspect(engine)
        tables = []
        
        for table_name in inspector.get_table_names():
            # Get column information
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": str(column.get("default", ""))
                })
            
            # Get primary key information
            pk = inspector.get_pk_constraint(table_name)
            
            # Get row count (with error handling)
            row_count = 0
            try:
                db = SessionLocal()
                result = db.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = result.scalar()
                db.close()
            except:
                pass
            
            tables.append({
                "name": table_name,
                "columns": columns,
                "primary_key": pk.get("constrained_columns", []) if pk else [],
                "row_count": row_count
            })
            
        return tables
    except Exception as e:
        logger.error(f"Failed to get schema info: {str(e)}")
        return []

# Knowledge Base endpoints
@app.post("/knowledge/design-concept", tags=["Knowledge Base"])
def add_design_concept(concept: DesignConceptCreate):
    """Add a new game design concept to the knowledge base."""
    try:
        kb = GameDesignKnowledgeBase()
        kb.add_design_concept(concept.name, concept.description, concept.examples, concept.references)
        return {"status": "success", "message": f"Added design concept: {concept.name}"}
    except Exception as e:
        logger.error(f"Error adding design concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/industry-practice", tags=["Knowledge Base"])
def add_industry_practice(practice: IndustryPracticeCreate):
    """Add a new industry practice to the knowledge base."""
    try:
        kb = GameDesignKnowledgeBase()
        kb.add_industry_practice(practice.name, practice.description, practice.companies, practice.outcomes)
        return {"status": "success", "message": f"Added industry practice: {practice.name}"}
    except Exception as e:
        logger.error(f"Error adding industry practice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/educational-resource", tags=["Knowledge Base"])
def add_educational_resource(resource: EducationalResourceCreate):
    """Add a new educational resource to the knowledge base."""
    try:
        kb = GameDesignKnowledgeBase()
        kb.add_educational_resource(resource.title, resource.type, resource.url, resource.description, resource.topics)
        return {"status": "success", "message": f"Added educational resource: {resource.title}"}
    except Exception as e:
        logger.error(f"Error adding educational resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/market-research", tags=["Knowledge Base"])
def add_market_research(research: MarketResearchCreate):
    """Add new market research to the knowledge base."""
    try:
        kb = GameDesignKnowledgeBase()
        kb.add_market_research(research.title, research.date, research.source, research.findings, research.implications)
        return {"status": "success", "message": f"Added market research: {research.title}"}
    except Exception as e:
        logger.error(f"Error adding market research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/search", tags=["Knowledge Base"])
def search_knowledge_base(search: SearchQuery):
    """Search the knowledge base for relevant information."""
    try:
        kb = GameDesignKnowledgeBase()
        results = kb.search_knowledge_base(search.query, search.category)
        return {"status": "success", "results": results}
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Modified server startup to accept port from command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Thomas AI API server')
    parser.add_argument('--port', type=int, default=8002, help='Port to run the server on (default: 8002)')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='Host to run the server on (default: 0.0.0.0)')
    args = parser.parse_args()
    
    # Log server startup
    logger.info(f"Starting API server on {args.host}:{args.port}")
    
    # Check database connection before starting the server
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        sys.exit(1)
    
    # Start the server
    try:
        uvicorn.run(app, host=args.host, port=args.port)
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        sys.exit(1)
