from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from services.enhanced_knowledge_base import get_enhanced_knowledge_base
from database.db_manager import get_db
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("knowledge_endpoints")

# Create router
router = APIRouter(
    prefix="/v2/knowledge",
    tags=["Enhanced Knowledge Base"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for API requests and responses

# Taxonomy models
class TaxonomyNodeCreate(BaseModel):
    name: str
    description: str
    parent_id: Optional[int] = None

class TaxonomyNodeResponse(BaseModel):
    id: int
    name: str
    description: str
    level: int
    path: str
    parent_id: Optional[int] = None
    children: List["TaxonomyNodeResponse"] = []

# Concept models
class ConceptCreate(BaseModel):
    name: str = Field(..., description="Name of the game design concept")
    description: str = Field(..., description="Description of the concept")
    examples: Optional[str] = Field(None, description="Examples of the concept in games")
    references: Optional[str] = Field(None, description="References to sources")
    taxonomy_ids: List[int] = Field([], description="IDs of taxonomy nodes to assign this concept to")

class ConceptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[str] = None
    references: Optional[str] = None
    taxonomy_ids: Optional[List[int]] = None
    comment: Optional[str] = None

class ConceptResponse(BaseModel):
    id: int
    name: str
    description: str
    examples: Optional[str] = None
    references: Optional[str] = None
    is_verified: bool
    current_revision: int
    created_at: str
    updated_at: str
    taxonomies: List[TaxonomyNodeResponse] = []

# Practice models
class PracticeCreate(BaseModel):
    name: str = Field(..., description="Name of the industry practice")
    description: str = Field(..., description="Description of the practice")
    implementation: Optional[str] = Field(None, description="How to implement this practice")
    benefits: Optional[str] = Field(None, description="Benefits of the practice")
    challenges: Optional[str] = Field(None, description="Challenges of implementing the practice")
    case_studies: Optional[str] = Field(None, description="Case studies or examples")
    taxonomy_ids: List[int] = Field([], description="IDs of taxonomy nodes to assign this practice to")

class PracticeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    implementation: Optional[str] = None
    benefits: Optional[str] = None
    challenges: Optional[str] = None
    case_studies: Optional[str] = None
    taxonomy_ids: Optional[List[int]] = None
    comment: Optional[str] = None

class PracticeResponse(BaseModel):
    id: int
    name: str
    description: str
    implementation: Optional[str] = None
    benefits: Optional[str] = None
    challenges: Optional[str] = None
    case_studies: Optional[str] = None
    is_verified: bool
    current_revision: int
    created_at: str
    updated_at: str
    taxonomies: List[TaxonomyNodeResponse] = []

# Resource models
class ResourceCreate(BaseModel):
    title: str = Field(..., description="Title of the educational resource")
    content_type: str = Field(..., description="Type of resource (Book, Course, Video, etc.)")
    description: str = Field(..., description="Description of the resource")
    url: Optional[str] = Field(None, description="URL to the resource")
    author: Optional[str] = Field(None, description="Author of the resource")
    publication_date: Optional[str] = Field(None, description="Publication date")
    summary: Optional[str] = Field(None, description="Summary of the resource")
    key_points: Optional[str] = Field(None, description="Key points from the resource")
    taxonomy_ids: List[int] = Field([], description="IDs of taxonomy nodes to assign this resource to")

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    content_type: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[str] = None
    taxonomy_ids: Optional[List[int]] = None
    comment: Optional[str] = None

class ResourceResponse(BaseModel):
    id: int
    title: str
    content_type: str
    description: str
    url: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[str] = None
    is_verified: bool
    current_revision: int
    created_at: str
    updated_at: str
    taxonomies: List[TaxonomyNodeResponse] = []

# Research models
class ResearchCreate(BaseModel):
    title: str = Field(..., description="Title of the market research")
    game_genre: Optional[str] = Field(None, description="Game genre the research applies to")
    platform: Optional[str] = Field(None, description="Platform the research applies to")
    target_audience: Optional[str] = Field(None, description="Target audience the research applies to")
    key_findings: str = Field(..., description="Key findings from the research")
    metrics: Optional[str] = Field(None, description="Metrics and data from the research")
    trends: Optional[str] = Field(None, description="Trends identified in the research")
    date_of_research: Optional[str] = Field(None, description="Date the research was conducted")
    taxonomy_ids: List[int] = Field([], description="IDs of taxonomy nodes to assign this research to")

class ResearchUpdate(BaseModel):
    title: Optional[str] = None
    game_genre: Optional[str] = None
    platform: Optional[str] = None
    target_audience: Optional[str] = None
    key_findings: Optional[str] = None
    metrics: Optional[str] = None
    trends: Optional[str] = None
    date_of_research: Optional[str] = None
    taxonomy_ids: Optional[List[int]] = None
    comment: Optional[str] = None

class ResearchResponse(BaseModel):
    id: int
    title: str
    game_genre: Optional[str] = None
    platform: Optional[str] = None
    target_audience: Optional[str] = None
    key_findings: str
    metrics: Optional[str] = None
    trends: Optional[str] = None
    date_of_research: Optional[str] = None
    is_verified: bool
    current_revision: int
    created_at: str
    updated_at: str
    taxonomies: List[TaxonomyNodeResponse] = []

# Search models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    content_types: Optional[List[str]] = Field(None, description="Types of content to search (concept, practice, resource, research)")
    max_results: int = Field(10, description="Maximum number of search results")
    use_semantic: bool = Field(True, description="Whether to use semantic search")

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Search results")

# Collaboration models
class LockRequest(BaseModel):
    content_type: str = Field(..., description="Type of content (concept, practice, resource, research)")
    content_id: int = Field(..., description="ID of the content item")
    user_id: str = Field(..., description="ID of the user locking the content")
    lock_duration_minutes: int = Field(30, description="Duration of the lock in minutes")

class UnlockRequest(BaseModel):
    content_type: str = Field(..., description="Type of content (concept, practice, resource, research)")
    content_id: int = Field(..., description="ID of the content item")
    user_id: str = Field(..., description="ID of the user unlocking the content")

class ReviewRequest(BaseModel):
    content_type: str = Field(..., description="Type of content (concept, practice, resource, research)")
    content_id: int = Field(..., description="ID of the content item")
    user_id: str = Field(..., description="ID of the user requesting review")
    reviewer_id: str = Field(..., description="ID of the reviewer")

class ReviewCompleteRequest(BaseModel):
    content_type: str = Field(..., description="Type of content (concept, practice, resource, research)")
    content_id: int = Field(..., description="ID of the content item")
    reviewer_id: str = Field(..., description="ID of the reviewer")
    approved: bool = Field(..., description="Whether the content is approved")
    comments: Optional[str] = Field(None, description="Comments on the review")

class CollaborationStatusResponse(BaseModel):
    is_locked: bool
    locked_by: Optional[str] = None
    lock_expires_at: Optional[str] = None
    in_review: bool
    reviewer_id: Optional[str] = None
    review_requested_at: Optional[str] = None
    review_completed_at: Optional[str] = None
    review_status: Optional[str] = None
    review_comments: Optional[str] = None

# Relationship models
class ConceptRelationshipCreate(BaseModel):
    source_id: int = Field(..., description="ID of the source concept")
    target_id: int = Field(..., description="ID of the target concept")
    relationship_type: str = Field("related", description="Type of relationship")

class RelatedConceptsResponse(BaseModel):
    concepts: List[Dict[str, Any]] = Field(..., description="Related concepts")

# API routes

# Taxonomy endpoints
@router.post("/taxonomy", response_model=int, summary="Create a new taxonomy node")
async def create_taxonomy_node(
    node: TaxonomyNodeCreate,
    db: Session = Depends(get_db)
):
    """Create a new taxonomy node, optionally as a child of another node"""
    try:
        kb = get_enhanced_knowledge_base()
        node_id = kb.create_taxonomy_node(node.name, node.description, node.parent_id)
        return node_id
    except Exception as e:
        logger.error(f"Error creating taxonomy node: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/taxonomy/{taxonomy_id}", response_model=Dict[str, Any], summary="Get a taxonomy node and its children")
async def get_taxonomy_subtree(
    taxonomy_id: int,
    db: Session = Depends(get_db)
):
    """Get a taxonomy node and its subtree"""
    try:
        kb = get_enhanced_knowledge_base()
        tree = kb.get_taxonomy_tree(taxonomy_id)
        if not tree:
            raise HTTPException(status_code=404, detail=f"Taxonomy node {taxonomy_id} not found")
        return tree[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting taxonomy tree: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/taxonomy", response_model=List[Dict[str, Any]], summary="Get the full taxonomy tree")
async def get_taxonomy_tree(
    db: Session = Depends(get_db)
):
    """Get the full taxonomy tree"""
    try:
        kb = get_enhanced_knowledge_base()
        tree = kb.get_taxonomy_tree()
        return tree
    except Exception as e:
        logger.error(f"Error getting taxonomy tree: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Concept endpoints
@router.post("/concepts", response_model=int, summary="Create a new game design concept")
async def create_concept(
    concept: ConceptCreate,
    db: Session = Depends(get_db)
):
    """Create a new game design concept"""
    try:
        # Implementation details omitted
        # This would create a new concept and return its ID
        return 1  # Placeholder return
    except Exception as e:
        logger.error(f"Error creating concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoint
@router.post("/search", response_model=SearchResponse, summary="Search the knowledge base")
async def search_knowledge(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search the knowledge base for content matching the query"""
    try:
        kb = get_enhanced_knowledge_base()
        results = kb.search(
            search_request.query, 
            search_request.content_types,
            search_request.max_results,
            search_request.use_semantic
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Collaboration endpoints
@router.post("/lock", summary="Lock a content item for editing")
async def lock_content(
    lock_request: LockRequest,
    db: Session = Depends(get_db)
):
    """Lock a content item for editing by a specific user"""
    try:
        kb = get_enhanced_knowledge_base()
        success = kb.lock_content(
            lock_request.content_type,
            lock_request.content_id,
            lock_request.user_id,
            lock_request.lock_duration_minutes
        )
        if not success:
            raise HTTPException(status_code=409, detail="The content is already locked by another user")
        return {"status": "success", "message": "Content locked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error locking content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unlock", summary="Unlock a content item")
async def unlock_content(
    unlock_request: UnlockRequest,
    db: Session = Depends(get_db)
):
    """Unlock a content item that was previously locked"""
    try:
        kb = get_enhanced_knowledge_base()
        success = kb.unlock_content(
            unlock_request.content_type,
            unlock_request.content_id,
            unlock_request.user_id
        )
        if not success:
            raise HTTPException(status_code=403, detail="You don't have permission to unlock this content")
        return {"status": "success", "message": "Content unlocked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-review", summary="Request a review for a content item")
async def request_review(
    review_request: ReviewRequest,
    db: Session = Depends(get_db)
):
    """Request a review for a content item"""
    try:
        kb = get_enhanced_knowledge_base()
        success = kb.request_review(
            review_request.content_type,
            review_request.content_id,
            review_request.user_id,
            review_request.reviewer_id
        )
        if not success:
            raise HTTPException(status_code=403, detail="You don't have permission to request a review for this content")
        return {"status": "success", "message": "Review requested successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete-review", summary="Complete a review for a content item")
async def complete_review(
    review_complete: ReviewCompleteRequest,
    db: Session = Depends(get_db)
):
    """Complete a review for a content item"""
    try:
        kb = get_enhanced_knowledge_base()
        success = kb.complete_review(
            review_complete.content_type,
            review_complete.content_id,
            review_complete.reviewer_id,
            review_complete.approved,
            review_complete.comments
        )
        if not success:
            raise HTTPException(status_code=403, detail="You don't have permission to complete this review")
        return {"status": "success", "message": "Review completed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaboration-status/{content_type}/{content_id}", response_model=CollaborationStatusResponse)
async def get_collaboration_status(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get the collaboration status for a content item"""
    try:
        kb = get_enhanced_knowledge_base()
        status = kb.get_content_collaboration_status(content_type, content_id)
        return status
    except Exception as e:
        logger.error(f"Error getting collaboration status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Relationship endpoints
@router.post("/concepts/relationships", summary="Create a relationship between concepts")
async def create_concept_relationship(
    relationship: ConceptRelationshipCreate,
    db: Session = Depends(get_db)
):
    """Create a relationship between two game design concepts"""
    try:
        kb = get_enhanced_knowledge_base()
        success = kb.create_concept_relationship(
            relationship.source_id,
            relationship.target_id,
            relationship.relationship_type
        )
        return {"status": "success", "message": "Relationship created successfully"}
    except Exception as e:
        logger.error(f"Error creating concept relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/concepts/{concept_id}/relationships", response_model=RelatedConceptsResponse)
async def get_related_concepts(
    concept_id: int,
    db: Session = Depends(get_db)
):
    """Get concepts related to the specified concept"""
    try:
        kb = get_enhanced_knowledge_base()
        related = kb.get_related_concepts(concept_id)
        return {"concepts": related}
    except Exception as e:
        logger.error(f"Error getting related concepts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Embedding endpoints
@router.post("/create-embedding/{content_type}/{content_id}", summary="Create or update embedding for a content item")
async def create_embedding(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    """Create or update the embedding vector for a content item"""
    try:
        kb = get_enhanced_knowledge_base()
        success = kb.create_embedding(content_type, content_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create embedding")
        return {"status": "success", "message": "Embedding created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 