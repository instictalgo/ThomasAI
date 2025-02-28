import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from database.db_manager import Base

# Many-to-many association tables
concept_relationship = Table(
    "concept_relationship",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("game_design_concepts.id"), primary_key=True),
    Column("target_id", Integer, ForeignKey("game_design_concepts.id"), primary_key=True),
    Column("relationship_type", String(50)),
    Column("created_at", DateTime, default=datetime.datetime.utcnow)
)

concept_taxonomy = Table(
    "concept_taxonomy",
    Base.metadata,
    Column("concept_id", Integer, ForeignKey("game_design_concepts.id"), primary_key=True),
    Column("taxonomy_id", Integer, ForeignKey("taxonomies.id"), primary_key=True)
)

practice_taxonomy = Table(
    "practice_taxonomy",
    Base.metadata,
    Column("practice_id", Integer, ForeignKey("industry_practices.id"), primary_key=True),
    Column("taxonomy_id", Integer, ForeignKey("taxonomies.id"), primary_key=True)
)

resource_taxonomy = Table(
    "resource_taxonomy",
    Base.metadata,
    Column("resource_id", Integer, ForeignKey("educational_resources.id"), primary_key=True),
    Column("taxonomy_id", Integer, ForeignKey("taxonomies.id"), primary_key=True)
)

research_taxonomy = Table(
    "research_taxonomy",
    Base.metadata,
    Column("research_id", Integer, ForeignKey("market_research.id"), primary_key=True),
    Column("taxonomy_id", Integer, ForeignKey("taxonomies.id"), primary_key=True)
)

class TaxonomyNode(Base):
    """Taxonomy node for hierarchical organization of knowledge"""
    __tablename__ = "taxonomies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("taxonomies.id"), nullable=True)
    level = Column(Integer, default=0)  # Depth level in the hierarchy
    path = Column(String(255))  # Materialized path for efficient lookup
    
    # Relationships
    parent = relationship("TaxonomyNode", remote_side=[id], backref="children")
    concepts = relationship("GameDesignConcept", secondary=concept_taxonomy, back_populates="taxonomies")
    practices = relationship("IndustryPractice", secondary=practice_taxonomy, back_populates="taxonomies")
    resources = relationship("EducationalResource", secondary=resource_taxonomy, back_populates="taxonomies")
    research = relationship("MarketResearch", secondary=research_taxonomy, back_populates="taxonomies")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<TaxonomyNode(id={self.id}, name='{self.name}', level={self.level})>"

class KnowledgeRevision(Base):
    """Base model for tracking revisions of knowledge entries"""
    __tablename__ = "knowledge_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False)  # Type of content (concept, practice, etc.)
    content_id = Column(Integer, nullable=False)  # ID of the content in its respective table
    revision_number = Column(Integer, nullable=False)
    content_data = Column(JSON, nullable=False)  # Full content at this revision
    
    creator_id = Column(String(100))  # User who created this revision
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    comment = Column(Text)  # Comment about the changes in this revision

    def __repr__(self):
        return f"<KnowledgeRevision(id={self.id}, content_type='{self.content_type}', content_id={self.content_id}, revision={self.revision_number})>"

class Embedding(Base):
    """Embeddings for semantic search"""
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False)
    content_id = Column(Integer, nullable=False)
    vector = Column(JSON, nullable=False)  # JSON array of embedding values
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Embedding(id={self.id}, content_type='{self.content_type}', content_id={self.content_id})>"

class GameDesignConcept(Base):
    """Model for game design concepts"""
    __tablename__ = "game_design_concepts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    examples = Column(Text)
    references = Column(Text)
    
    # Metadata fields
    creator_id = Column(String(100))
    source = Column(String(255))
    confidence_score = Column(Float, default=1.0)  # Automatic entries can have lower confidence
    is_verified = Column(Boolean, default=False)
    current_revision = Column(Integer, default=1)
    
    # Relationships
    related_to = relationship(
        "GameDesignConcept", 
        secondary=concept_relationship,
        primaryjoin=id==concept_relationship.c.source_id,
        secondaryjoin=id==concept_relationship.c.target_id,
        backref="related_from"
    )
    taxonomies = relationship("TaxonomyNode", secondary=concept_taxonomy, back_populates="concepts")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<GameDesignConcept(id={self.id}, name='{self.name}')>"

class IndustryPractice(Base):
    """Model for industry practices"""
    __tablename__ = "industry_practices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    implementation = Column(Text)
    benefits = Column(Text)
    challenges = Column(Text)
    case_studies = Column(Text)
    
    # Metadata fields
    creator_id = Column(String(100))
    source = Column(String(255))
    confidence_score = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False)
    current_revision = Column(Integer, default=1)
    
    # Relationships
    taxonomies = relationship("TaxonomyNode", secondary=practice_taxonomy, back_populates="practices")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<IndustryPractice(id={self.id}, name='{self.name}')>"

class EducationalResource(Base):
    """Model for educational resources"""
    __tablename__ = "educational_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, unique=True)
    content_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String(512))
    author = Column(String(255))
    publication_date = Column(String(50))
    summary = Column(Text)
    key_points = Column(Text)
    
    # Metadata fields
    creator_id = Column(String(100))
    source = Column(String(255))
    confidence_score = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False)
    current_revision = Column(Integer, default=1)
    
    # Relationships
    taxonomies = relationship("TaxonomyNode", secondary=resource_taxonomy, back_populates="resources")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<EducationalResource(id={self.id}, title='{self.title}')>"

class MarketResearch(Base):
    """Model for market research"""
    __tablename__ = "market_research"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    game_genre = Column(String(100))
    platform = Column(String(100))
    target_audience = Column(String(100))
    key_findings = Column(Text, nullable=False)
    metrics = Column(Text)
    trends = Column(Text)
    date_of_research = Column(String(50))
    
    # Metadata fields
    creator_id = Column(String(100))
    source = Column(String(255))
    confidence_score = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False)
    current_revision = Column(Integer, default=1)
    
    # Relationships
    taxonomies = relationship("TaxonomyNode", secondary=research_taxonomy, back_populates="research")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<MarketResearch(id={self.id}, title='{self.title}')>"

class ContentCollaboration(Base):
    """Model for collaborative editing information"""
    __tablename__ = "content_collaboration"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False)
    content_id = Column(Integer, nullable=False)
    
    # Collaboration metadata
    locked_by = Column(String(100))  # User who has locked the content for editing
    lock_expires_at = Column(DateTime)
    
    # Review status
    in_review = Column(Boolean, default=False)
    reviewer_id = Column(String(100))
    review_requested_at = Column(DateTime)
    review_completed_at = Column(DateTime)
    review_status = Column(String(50))  # "approved", "rejected", "pending"
    review_comments = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ContentCollaboration(id={self.id}, content_type='{self.content_type}', content_id={self.content_id})>" 