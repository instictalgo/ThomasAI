from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
import enum
import datetime

# Import the shared Base
from models.base import Base

# Define an association table for asset dependencies
asset_dependency = Table(
    'asset_dependency', 
    Base.metadata,
    Column('dependent_id', Integer, ForeignKey('assets.id'), primary_key=True),
    Column('depends_on_id', Integer, ForeignKey('assets.id'), primary_key=True)
)

class AssetType(enum.Enum):
    MODEL_3D = "model_3d"
    ANIMATION = "animation"
    TEXTURE = "texture"
    SCRIPT = "script"
    SOUND = "sound"
    UI = "ui"
    LEVEL = "level"
    OTHER = "other"

class AssetStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETE = "complete"
    BLOCKED = "blocked"

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    asset_type = Column(String)
    status = Column(String, default="not_started")
    progress = Column(Integer, default=0)  # 0-100%
    assigned_to = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_date = Column(String, default=datetime.datetime.now().strftime("%Y-%m-%d"))
    due_date = Column(String, nullable=True)
    
    # Define relationships
    dependencies = relationship(
        "Asset", 
        secondary=asset_dependency,
        primaryjoin=(asset_dependency.c.dependent_id == id),
        secondaryjoin=(asset_dependency.c.depends_on_id == id),
        backref="dependents"
    )
    
    def to_dict(self):
        """Convert asset object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "asset_type": self.asset_type,
            "status": self.status,
            "progress": self.progress,
            "assigned_to": self.assigned_to,
            "project_id": self.project_id,
            "created_date": self.created_date,
            "due_date": self.due_date
        }
