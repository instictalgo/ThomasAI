import os
import json
import datetime
import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc
from dotenv import load_dotenv
import requests
from contextlib import contextmanager

from database.db_manager import SessionLocal
from models.knowledge_models import (
    GameDesignConcept, 
    IndustryPractice, 
    EducationalResource, 
    MarketResearch, 
    TaxonomyNode,
    KnowledgeRevision,
    ContentCollaboration,
    Embedding,
    concept_taxonomy,
    practice_taxonomy,
    resource_taxonomy,
    research_taxonomy
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_knowledge_base")

class EnhancedKnowledgeBase:
    """
    Enhanced knowledge base for Thomas AI with advanced features:
    - Version control and revision history
    - Taxonomy and hierarchical organization
    - Relationship mapping between concepts
    - Collaborative editing
    - Advanced search capabilities
    - Caching for improved performance
    """
    
    def __init__(self):
        """Initialize the knowledge base service"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.initialize_database()
        
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def initialize_database(self):
        """Initialize the database and create root taxonomy nodes if they don't exist"""
        with self.get_db_session() as db:
            # Create root taxonomy nodes for main categories
            root_taxonomies = [
                {"name": "Game Mechanics", "description": "Core interactive systems and rules"},
                {"name": "Game Design Patterns", "description": "Recurring solutions to common game design problems"},
                {"name": "Monetization", "description": "Revenue generation strategies"},
                {"name": "Player Psychology", "description": "Understanding player behavior and motivation"},
                {"name": "Technical Implementation", "description": "Technical aspects of game development"},
                {"name": "Art & Aesthetics", "description": "Visual and audio design"},
                {"name": "Game Narrative", "description": "Storytelling and narrative design"},
                {"name": "Industry Trends", "description": "Current directions in the game industry"}
            ]
            
            for tax in root_taxonomies:
                existing = db.query(TaxonomyNode).filter(TaxonomyNode.name == tax["name"]).first()
                if not existing:
                    new_node = TaxonomyNode(
                        name=tax["name"],
                        description=tax["description"],
                        level=0,
                        path=tax["name"]
                    )
                    db.add(new_node)
            
            db.commit()
            logger.info("Database initialized with root taxonomy nodes")
            
    # Taxonomy Management Methods
    
    def create_taxonomy_node(self, name: str, description: str, parent_id: Optional[int] = None) -> int:
        """
        Create a new taxonomy node, optionally as a child of another node
        
        Args:
            name: Name of the taxonomy node
            description: Description of the node
            parent_id: Optional parent node ID
            
        Returns:
            int: ID of the new taxonomy node
        """
        with self.get_db_session() as db:
            # Check if node with this name already exists
            existing = db.query(TaxonomyNode).filter(TaxonomyNode.name == name).first()
            if existing:
                return existing.id
            
            # If parent_id is provided, get the parent node
            parent = None
            if parent_id:
                parent = db.query(TaxonomyNode).filter(TaxonomyNode.id == parent_id).first()
                if not parent:
                    raise ValueError(f"Parent taxonomy node with ID {parent_id} not found")
            
            # Create new node
            level = 0
            path = name
            if parent:
                level = parent.level + 1
                path = f"{parent.path}/{name}"
            
            new_node = TaxonomyNode(
                name=name,
                description=description,
                parent_id=parent_id,
                level=level,
                path=path
            )
            
            db.add(new_node)
            db.commit()
            db.refresh(new_node)
            
            logger.info(f"Created taxonomy node: {name} (ID: {new_node.id})")
            return new_node.id
    
    def get_taxonomy_tree(self, root_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the taxonomy tree starting from the specified root node
        
        Args:
            root_id: Optional root taxonomy node ID. If None, return the entire tree.
            
        Returns:
            List of taxonomy nodes in a hierarchical structure
        """
        with self.get_db_session() as db:
            if root_id:
                # Get the root node and its children
                root = db.query(TaxonomyNode).filter(TaxonomyNode.id == root_id).first()
                if not root:
                    return []
                
                # Get all nodes that have a path starting with the root path
                nodes = db.query(TaxonomyNode).filter(
                    TaxonomyNode.path.like(f"{root.path}%")
                ).order_by(asc(TaxonomyNode.level), asc(TaxonomyNode.name)).all()
            else:
                # Get all nodes
                nodes = db.query(TaxonomyNode).order_by(
                    asc(TaxonomyNode.level), asc(TaxonomyNode.name)
                ).all()
            
            # Build the tree
            tree = []
            node_map = {}
            
            for node in nodes:
                node_data = {
                    "id": node.id,
                    "name": node.name,
                    "description": node.description,
                    "level": node.level,
                    "path": node.path,
                    "children": []
                }
                
                node_map[node.id] = node_data
                
                if node.parent_id and node.parent_id in node_map:
                    # Add to parent's children
                    node_map[node.parent_id]["children"].append(node_data)
                else:
                    # This is a root node or parent not in the current set
                    tree.append(node_data)
            
            return tree
    
    def assign_to_taxonomy(self, content_type: str, content_id: int, taxonomy_ids: List[int]) -> bool:
        """
        Assign a content item to one or more taxonomy nodes
        
        Args:
            content_type: Type of content ("concept", "practice", "resource", "research")
            content_id: ID of the content item
            taxonomy_ids: List of taxonomy node IDs to assign the content to
            
        Returns:
            bool: Success status
        """
        with self.get_db_session() as db:
            # Validate the content exists
            if content_type == "concept":
                content = db.query(GameDesignConcept).filter(GameDesignConcept.id == content_id).first()
                if not content:
                    raise ValueError(f"Game design concept with ID {content_id} not found")
            elif content_type == "practice":
                content = db.query(IndustryPractice).filter(IndustryPractice.id == content_id).first()
                if not content:
                    raise ValueError(f"Industry practice with ID {content_id} not found")
            elif content_type == "resource":
                content = db.query(EducationalResource).filter(EducationalResource.id == content_id).first()
                if not content:
                    raise ValueError(f"Educational resource with ID {content_id} not found")
            elif content_type == "research":
                content = db.query(MarketResearch).filter(MarketResearch.id == content_id).first()
                if not content:
                    raise ValueError(f"Market research with ID {content_id} not found")
            else:
                raise ValueError(f"Invalid content type: {content_type}")
            
            # Validate taxonomy nodes exist
            for tax_id in taxonomy_ids:
                tax_node = db.query(TaxonomyNode).filter(TaxonomyNode.id == tax_id).first()
                if not tax_node:
                    raise ValueError(f"Taxonomy node with ID {tax_id} not found")
            
            # Clear existing taxonomy assignments
            if content_type == "concept":
                statement = concept_taxonomy.delete().where(concept_taxonomy.c.concept_id == content_id)
                db.execute(statement)
                
                # Add new assignments
                for tax_id in taxonomy_ids:
                    db.execute(
                        concept_taxonomy.insert().values(concept_id=content_id, taxonomy_id=tax_id)
                    )
            elif content_type == "practice":
                statement = practice_taxonomy.delete().where(practice_taxonomy.c.practice_id == content_id)
                db.execute(statement)
                
                # Add new assignments
                for tax_id in taxonomy_ids:
                    db.execute(
                        practice_taxonomy.insert().values(practice_id=content_id, taxonomy_id=tax_id)
                    )
            elif content_type == "resource":
                statement = resource_taxonomy.delete().where(resource_taxonomy.c.resource_id == content_id)
                db.execute(statement)
                
                # Add new assignments
                for tax_id in taxonomy_ids:
                    db.execute(
                        resource_taxonomy.insert().values(resource_id=content_id, taxonomy_id=tax_id)
                    )
            elif content_type == "research":
                statement = research_taxonomy.delete().where(research_taxonomy.c.research_id == content_id)
                db.execute(statement)
                
                # Add new assignments
                for tax_id in taxonomy_ids:
                    db.execute(
                        research_taxonomy.insert().values(research_id=content_id, taxonomy_id=tax_id)
                    )
            
            db.commit()
            logger.info(f"Assigned {content_type} (ID: {content_id}) to taxonomy nodes: {taxonomy_ids}")
            return True
    
    # Version Control Methods
    
    def create_revision(self, content_type: str, content_id: int, content_data: Dict[str, Any], 
                        creator_id: Optional[str] = None, comment: Optional[str] = None) -> int:
        """
        Create a new revision for a content item
        
        Args:
            content_type: Type of content ("concept", "practice", "resource", "research")
            content_id: ID of the content item
            content_data: Full content data at this revision
            creator_id: Optional ID of the user creating this revision
            comment: Optional comment about the changes
            
        Returns:
            int: Revision number
        """
        with self.get_db_session() as db:
            # Get the current revision number
            current_revision = db.query(func.max(KnowledgeRevision.revision_number)).filter(
                KnowledgeRevision.content_type == content_type,
                KnowledgeRevision.content_id == content_id
            ).scalar() or 0
            
            # Create new revision
            new_revision = current_revision + 1
            
            revision = KnowledgeRevision(
                content_type=content_type,
                content_id=content_id,
                revision_number=new_revision,
                content_data=content_data,
                creator_id=creator_id,
                comment=comment
            )
            
            db.add(revision)
            
            # Update the current_revision field in the content item
            if content_type == "concept":
                db.query(GameDesignConcept).filter(
                    GameDesignConcept.id == content_id
                ).update({"current_revision": new_revision})
            elif content_type == "practice":
                db.query(IndustryPractice).filter(
                    IndustryPractice.id == content_id
                ).update({"current_revision": new_revision})
            elif content_type == "resource":
                db.query(EducationalResource).filter(
                    EducationalResource.id == content_id
                ).update({"current_revision": new_revision})
            elif content_type == "research":
                db.query(MarketResearch).filter(
                    MarketResearch.id == content_id
                ).update({"current_revision": new_revision})
            
            db.commit()
            db.refresh(revision)
            
            logger.info(f"Created revision {new_revision} for {content_type} (ID: {content_id})")
            return new_revision
    
    def get_revision_history(self, content_type: str, content_id: int) -> List[Dict[str, Any]]:
        """
        Get the revision history for a content item
        
        Args:
            content_type: Type of content ("concept", "practice", "resource", "research")
            content_id: ID of the content item
            
        Returns:
            List of revisions with metadata
        """
        with self.get_db_session() as db:
            revisions = db.query(KnowledgeRevision).filter(
                KnowledgeRevision.content_type == content_type,
                KnowledgeRevision.content_id == content_id
            ).order_by(desc(KnowledgeRevision.revision_number)).all()
            
            result = []
            for rev in revisions:
                result.append({
                    "revision": rev.revision_number,
                    "created_at": rev.created_at.isoformat(),
                    "creator_id": rev.creator_id,
                    "comment": rev.comment
                })
            
            return result
    
    def get_revision_content(self, content_type: str, content_id: int, revision: int) -> Dict[str, Any]:
        """
        Get the content data at a specific revision
        
        Args:
            content_type: Type of content ("concept", "practice", "resource", "research")
            content_id: ID of the content item
            revision: Revision number
            
        Returns:
            Content data at the specified revision
        """
        with self.get_db_session() as db:
            rev = db.query(KnowledgeRevision).filter(
                KnowledgeRevision.content_type == content_type,
                KnowledgeRevision.content_id == content_id,
                KnowledgeRevision.revision_number == revision
            ).first()
            
            if not rev:
                raise ValueError(f"Revision {revision} not found for {content_type} (ID: {content_id})")
            
            return rev.content_data
    
    def revert_to_revision(self, content_type: str, content_id: int, revision: int, 
                          creator_id: Optional[str] = None) -> int:
        """
        Revert a content item to a previous revision
        
        Args:
            content_type: Type of content ("concept", "practice", "resource", "research")
            content_id: ID of the content item
            revision: Revision number to revert to
            creator_id: Optional ID of the user performing the revert
            
        Returns:
            int: New revision number after the revert
        """
        with self.get_db_session() as db:
            # Get the revision data
            rev = db.query(KnowledgeRevision).filter(
                KnowledgeRevision.content_type == content_type,
                KnowledgeRevision.content_id == content_id,
                KnowledgeRevision.revision_number == revision
            ).first()
            
            if not rev:
                raise ValueError(f"Revision {revision} not found for {content_type} (ID: {content_id})")
            
            # Create a new revision with the old content
            new_revision = self.create_revision(
                content_type=content_type,
                content_id=content_id,
                content_data=rev.content_data,
                creator_id=creator_id,
                comment=f"Reverted to revision {revision}"
            )
            
            # Update the content item with the data from the old revision
            if content_type == "concept":
                # Update fields from the revision data
                content = db.query(GameDesignConcept).filter(GameDesignConcept.id == content_id).first()
                for key, value in rev.content_data.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
            elif content_type == "practice":
                content = db.query(IndustryPractice).filter(IndustryPractice.id == content_id).first()
                for key, value in rev.content_data.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
            elif content_type == "resource":
                content = db.query(EducationalResource).filter(EducationalResource.id == content_id).first()
                for key, value in rev.content_data.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
            elif content_type == "research":
                content = db.query(MarketResearch).filter(MarketResearch.id == content_id).first()
                for key, value in rev.content_data.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
            
            db.commit()
            
            logger.info(f"Reverted {content_type} (ID: {content_id}) to revision {revision}, created new revision {new_revision}")
            return new_revision
    
    # Collaborative Editing Methods
    
    def lock_content(self, content_type: str, content_id: int, user_id: str, 
                    lock_duration_minutes: int = 30) -> bool:
        """
        Lock a content item for editing by a specific user
        
        Args:
            content_type: Type of content ("concept", "practice", "resource", "research")
            content_id: ID of the content item
            user_id: ID of the user locking the content
            lock_duration_minutes: How long the lock should last
            
        Returns:
            bool: Whether the lock was successful
        """
        with self.get_db_session() as db:
            # Check if the content is already locked
            collab = db.query(ContentCollaboration).filter(
                ContentCollaboration.content_type == content_type,
                ContentCollaboration.content_id == content_id
            ).first()
            
            now = datetime.datetime.utcnow()
            expiration = now + datetime.timedelta(minutes=lock_duration_minutes)
            
            if collab:
                # If lock exists and hasn't expired
                if collab.locked_by and collab.lock_expires_at and collab.lock_expires_at > now:
                    # Cannot lock if someone else has it locked
                    if collab.locked_by != user_id:
                        return False
                
                # Update the lock
                collab.locked_by = user_id
                collab.lock_expires_at = expiration
            else:
                # Create new collaboration record
                collab = ContentCollaboration(
                    content_type=content_type,
                    content_id=content_id,
                    locked_by=user_id,
                    lock_expires_at=expiration
                )
                db.add(collab)
            
            db.commit()
            logger.info(f"Locked {content_type} (ID: {content_id}) for editing by user {user_id}")
            return True
    
    def unlock_content(self, content_type: str, content_id: int, user_id: str) -> bool:
        """
        Unlock a content item
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            user_id: ID of the user unlocking the content (must be the same user who locked it)
            
        Returns:
            bool: Whether the unlock was successful
        """
        with self.get_db_session() as db:
            collab = db.query(ContentCollaboration).filter(
                ContentCollaboration.content_type == content_type,
                ContentCollaboration.content_id == content_id,
                ContentCollaboration.locked_by == user_id
            ).first()
            
            if not collab:
                return False
            
            collab.locked_by = None
            collab.lock_expires_at = None
            
            db.commit()
            logger.info(f"Unlocked {content_type} (ID: {content_id}) by user {user_id}")
            return True
    
    def request_review(self, content_type: str, content_id: int, 
                      user_id: str, reviewer_id: str) -> bool:
        """
        Request a review for a content item
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            user_id: ID of the user requesting review
            reviewer_id: ID of the user who should review
            
        Returns:
            bool: Whether the review request was successful
        """
        with self.get_db_session() as db:
            collab = db.query(ContentCollaboration).filter(
                ContentCollaboration.content_type == content_type,
                ContentCollaboration.content_id == content_id
            ).first()
            
            now = datetime.datetime.utcnow()
            
            if collab:
                # Only the person who has it locked can request review
                if collab.locked_by and collab.locked_by != user_id:
                    return False
                
                collab.in_review = True
                collab.reviewer_id = reviewer_id
                collab.review_requested_at = now
                collab.review_status = "pending"
                # Unlock the content when requesting review
                collab.locked_by = None
                collab.lock_expires_at = None
            else:
                # Create new collaboration record
                collab = ContentCollaboration(
                    content_type=content_type,
                    content_id=content_id,
                    in_review=True,
                    reviewer_id=reviewer_id,
                    review_requested_at=now,
                    review_status="pending"
                )
                db.add(collab)
            
            db.commit()
            logger.info(f"Requested review for {content_type} (ID: {content_id}) by user {reviewer_id}")
            return True
    
    def complete_review(self, content_type: str, content_id: int, 
                       reviewer_id: str, approved: bool, comments: Optional[str] = None) -> bool:
        """
        Complete a review for a content item
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            reviewer_id: ID of the reviewer
            approved: Whether the content is approved
            comments: Optional review comments
            
        Returns:
            bool: Whether the review completion was successful
        """
        with self.get_db_session() as db:
            collab = db.query(ContentCollaboration).filter(
                ContentCollaboration.content_type == content_type,
                ContentCollaboration.content_id == content_id,
                ContentCollaboration.reviewer_id == reviewer_id,
                ContentCollaboration.in_review == True
            ).first()
            
            if not collab:
                return False
            
            now = datetime.datetime.utcnow()
            collab.review_completed_at = now
            collab.review_status = "approved" if approved else "rejected"
            collab.review_comments = comments
            collab.in_review = False
            
            # If approved, update the verification status of the content
            if approved:
                if content_type == "concept":
                    db.query(GameDesignConcept).filter(
                        GameDesignConcept.id == content_id
                    ).update({"is_verified": True})
                elif content_type == "practice":
                    db.query(IndustryPractice).filter(
                        IndustryPractice.id == content_id
                    ).update({"is_verified": True})
                elif content_type == "resource":
                    db.query(EducationalResource).filter(
                        EducationalResource.id == content_id
                    ).update({"is_verified": True})
                elif content_type == "research":
                    db.query(MarketResearch).filter(
                        MarketResearch.id == content_id
                    ).update({"is_verified": True})
            
            db.commit()
            logger.info(f"Completed review for {content_type} (ID: {content_id}) by {reviewer_id}, status: {collab.review_status}")
            return True
    
    def get_content_collaboration_status(self, content_type: str, content_id: int) -> Dict[str, Any]:
        """
        Get the collaboration status for a content item
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            
        Returns:
            Collaboration status data
        """
        with self.get_db_session() as db:
            collab = db.query(ContentCollaboration).filter(
                ContentCollaboration.content_type == content_type,
                ContentCollaboration.content_id == content_id
            ).first()
            
            if not collab:
                return {
                    "is_locked": False,
                    "in_review": False,
                    "review_status": None
                }
            
            now = datetime.datetime.utcnow()
            is_locked = collab.locked_by is not None and collab.lock_expires_at and collab.lock_expires_at > now
            
            return {
                "is_locked": is_locked,
                "locked_by": collab.locked_by if is_locked else None,
                "lock_expires_at": collab.lock_expires_at.isoformat() if is_locked and collab.lock_expires_at else None,
                "in_review": collab.in_review,
                "reviewer_id": collab.reviewer_id,
                "review_requested_at": collab.review_requested_at.isoformat() if collab.review_requested_at else None,
                "review_completed_at": collab.review_completed_at.isoformat() if collab.review_completed_at else None,
                "review_status": collab.review_status,
                "review_comments": collab.review_comments
            }
    
    # Content Relationship Methods
    
    def create_concept_relationship(self, source_id: int, target_id: int, 
                                   relationship_type: str = "related") -> bool:
        """
        Create a relationship between two game design concepts
        
        Args:
            source_id: ID of the source concept
            target_id: ID of the target concept
            relationship_type: Type of relationship
            
        Returns:
            bool: Success status
        """
        with self.get_db_session() as db:
            # Verify both concepts exist
            source = db.query(GameDesignConcept).filter(GameDesignConcept.id == source_id).first()
            if not source:
                raise ValueError(f"Source concept with ID {source_id} not found")
            
            target = db.query(GameDesignConcept).filter(GameDesignConcept.id == target_id).first()
            if not target:
                raise ValueError(f"Target concept with ID {target_id} not found")
            
            # Add the relationship
            db.execute(
                concept_relationship.insert().values(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=relationship_type
                )
            )
            
            db.commit()
            logger.info(f"Created relationship from concept {source_id} to concept {target_id} of type '{relationship_type}'")
            return True
    
    def get_related_concepts(self, concept_id: int) -> List[Dict[str, Any]]:
        """
        Get concepts related to the specified concept
        
        Args:
            concept_id: ID of the concept
            
        Returns:
            List of related concepts with relationship metadata
        """
        with self.get_db_session() as db:
            # Get concepts that this concept is related to
            related_to_stmt = db.query(
                GameDesignConcept,
                concept_relationship.c.relationship_type
            ).join(
                concept_relationship,
                and_(
                    concept_relationship.c.target_id == GameDesignConcept.id,
                    concept_relationship.c.source_id == concept_id
                )
            )
            
            # Get concepts that are related to this concept
            related_from_stmt = db.query(
                GameDesignConcept,
                concept_relationship.c.relationship_type
            ).join(
                concept_relationship,
                and_(
                    concept_relationship.c.source_id == GameDesignConcept.id,
                    concept_relationship.c.target_id == concept_id
                )
            )
            
            related_to = [(concept, rel_type, "to") for concept, rel_type in related_to_stmt]
            related_from = [(concept, rel_type, "from") for concept, rel_type in related_from_stmt]
            
            related = related_to + related_from
            
            result = []
            for concept, rel_type, direction in related:
                result.append({
                    "id": concept.id,
                    "name": concept.name,
                    "relationship_type": rel_type,
                    "direction": direction
                })
            
            return result
    
    # Enhanced Search Methods
    
    def create_embedding(self, content_type: str, content_id: int) -> bool:
        """
        Create or update embedding vector for a content item
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            
        Returns:
            bool: Success status
        """
        if not self.openai_api_key:
            logger.warning("Cannot create embedding: No OpenAI API key provided")
            return False
        
        with self.get_db_session() as db:
            # Get the content text to embed
            text_to_embed = ""
            
            if content_type == "concept":
                concept = db.query(GameDesignConcept).filter(GameDesignConcept.id == content_id).first()
                if not concept:
                    raise ValueError(f"Concept with ID {content_id} not found")
                text_to_embed = f"{concept.name}: {concept.description}"
                if concept.examples:
                    text_to_embed += f" Examples: {concept.examples}"
            
            elif content_type == "practice":
                practice = db.query(IndustryPractice).filter(IndustryPractice.id == content_id).first()
                if not practice:
                    raise ValueError(f"Practice with ID {content_id} not found")
                text_to_embed = f"{practice.name}: {practice.description}"
                if practice.implementation:
                    text_to_embed += f" Implementation: {practice.implementation}"
                if practice.benefits:
                    text_to_embed += f" Benefits: {practice.benefits}"
            
            elif content_type == "resource":
                resource = db.query(EducationalResource).filter(EducationalResource.id == content_id).first()
                if not resource:
                    raise ValueError(f"Resource with ID {content_id} not found")
                text_to_embed = f"{resource.title}: {resource.description}"
                if resource.summary:
                    text_to_embed += f" Summary: {resource.summary}"
                if resource.key_points:
                    text_to_embed += f" Key Points: {resource.key_points}"
            
            elif content_type == "research":
                research = db.query(MarketResearch).filter(MarketResearch.id == content_id).first()
                if not research:
                    raise ValueError(f"Research with ID {content_id} not found")
                text_to_embed = f"{research.title}: {research.key_findings}"
                if research.trends:
                    text_to_embed += f" Trends: {research.trends}"
            
            else:
                raise ValueError(f"Invalid content type: {content_type}")
            
            if not text_to_embed:
                logger.warning(f"No text to embed for {content_type} (ID: {content_id})")
                return False
            
            # Call OpenAI API to get embedding
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "input": text_to_embed[:8000],  # Limit text length to avoid token limits
                    "model": "text-embedding-ada-002"  # Use the latest embedding model
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Error creating embedding: {response.text}")
                    return False
                
                embedding_data = response.json()
                embedding_vector = embedding_data["data"][0]["embedding"]
                
                # Store or update the embedding
                existing = db.query(Embedding).filter(
                    Embedding.content_type == content_type,
                    Embedding.content_id == content_id
                ).first()
                
                if existing:
                    existing.vector = embedding_vector
                    existing.updated_at = datetime.datetime.utcnow()
                else:
                    embedding = Embedding(
                        content_type=content_type,
                        content_id=content_id,
                        vector=embedding_vector
                    )
                    db.add(embedding)
                
                db.commit()
                logger.info(f"Created embedding for {content_type} (ID: {content_id})")
                return True
            
            except Exception as e:
                logger.error(f"Error creating embedding: {str(e)}")
                return False
    
    def search(self, query: str, content_types: Optional[List[str]] = None, 
              max_results: int = 10, use_semantic: bool = True) -> List[Dict[str, Any]]:
        """
        Search the knowledge base using a combination of keyword and semantic search
        
        Args:
            query: Search query
            content_types: Optional list of content types to search
            max_results: Maximum number of results to return
            use_semantic: Whether to use semantic search (requires OpenAI API key)
            
        Returns:
            List of search results
        """
        # Get results from cache if available
        cache_key = f"search:{query}:{content_types}:{max_results}:{use_semantic}"
        if cache_key in self.cache:
            cache_time, cache_results = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cache_results
        
        if not content_types:
            content_types = ["concept", "practice", "resource", "research"]
        
        # Normalize content types
        valid_types = {
            "concept": GameDesignConcept,
            "practice": IndustryPractice,
            "resource": EducationalResource,
            "research": MarketResearch
        }
        
        types_to_search = []
        for ct in content_types:
            if ct in valid_types:
                types_to_search.append((ct, valid_types[ct]))
        
        # If no valid types, return empty result
        if not types_to_search:
            return []
        
        # Start with keyword search
        keyword_results = self._keyword_search(query, types_to_search, max_results)
        
        # If semantic search is enabled and we have an API key, combine with semantic results
        if use_semantic and self.openai_api_key and len(query) > 5:
            semantic_results = self._semantic_search(query, types_to_search, max_results)
            
            # Combine results with ranking
            combined_results = self._combine_search_results(keyword_results, semantic_results)
            results = combined_results[:max_results]
        else:
            results = keyword_results[:max_results]
        
        # Cache the results
        self.cache[cache_key] = (time.time(), results)
        
        return results
    
    def _keyword_search(self, query: str, types_to_search: List[Tuple[str, Any]], 
                       max_results: int) -> List[Dict[str, Any]]:
        """Perform keyword-based search"""
        results = []
        
        # Split query into keywords
        keywords = query.lower().split()
        
        with self.get_db_session() as db:
            for content_type, model_class in types_to_search:
                # Build search condition for each keyword
                conditions = []
                
                # For concepts
                if content_type == "concept":
                    for keyword in keywords:
                        conditions.append(or_(
                            func.lower(model_class.name).contains(keyword),
                            func.lower(model_class.description).contains(keyword),
                            func.lower(model_class.examples).contains(keyword) if model_class.examples else False
                        ))
                
                # For practices
                elif content_type == "practice":
                    for keyword in keywords:
                        conditions.append(or_(
                            func.lower(model_class.name).contains(keyword),
                            func.lower(model_class.description).contains(keyword),
                            func.lower(model_class.implementation).contains(keyword) if model_class.implementation else False,
                            func.lower(model_class.benefits).contains(keyword) if model_class.benefits else False,
                            func.lower(model_class.challenges).contains(keyword) if model_class.challenges else False
                        ))
                
                # For resources
                elif content_type == "resource":
                    for keyword in keywords:
                        conditions.append(or_(
                            func.lower(model_class.title).contains(keyword),
                            func.lower(model_class.description).contains(keyword),
                            func.lower(model_class.summary).contains(keyword) if model_class.summary else False,
                            func.lower(model_class.key_points).contains(keyword) if model_class.key_points else False
                        ))
                
                # For research
                elif content_type == "research":
                    for keyword in keywords:
                        conditions.append(or_(
                            func.lower(model_class.title).contains(keyword),
                            func.lower(model_class.key_findings).contains(keyword),
                            func.lower(model_class.trends).contains(keyword) if model_class.trends else False
                        ))
                
                # Get matching items that satisfy all keyword conditions
                items = db.query(model_class).filter(and_(*conditions)).all()
                
                # Transform to result format
                for item in items:
                    result = {
                        "id": item.id,
                        "type": content_type,
                        "score": 1.0,  # Base score
                        "data": {}
                    }
                    
                    # Add fields based on content type
                    if content_type == "concept":
                        result["data"] = {
                            "name": item.name,
                            "description": item.description,
                            "examples": item.examples,
                            "is_verified": item.is_verified
                        }
                    elif content_type == "practice":
                        result["data"] = {
                            "name": item.name,
                            "description": item.description,
                            "implementation": item.implementation,
                            "benefits": item.benefits,
                            "is_verified": item.is_verified
                        }
                    elif content_type == "resource":
                        result["data"] = {
                            "title": item.title,
                            "type": item.content_type,
                            "description": item.description,
                            "url": item.url,
                            "is_verified": item.is_verified
                        }
                    elif content_type == "research":
                        result["data"] = {
                            "title": item.title,
                            "key_findings": item.key_findings,
                            "date": item.date_of_research,
                            "is_verified": item.is_verified
                        }
                    
                    results.append(result)
        
        return results
    
    def _semantic_search(self, query: str, types_to_search: List[Tuple[str, Any]], 
                        max_results: int) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings"""
        if not self.openai_api_key:
            return []
        
        try:
            # Get embedding for the query
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": query,
                "model": "text-embedding-ada-002"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting query embedding: {response.text}")
                return []
            
            query_embedding = response.json()["data"][0]["embedding"]
            
            results = []
            
            with self.get_db_session() as db:
                for content_type, model_class in types_to_search:
                    # Get embeddings for this content type
                    embeddings = db.query(Embedding).filter(
                        Embedding.content_type == content_type
                    ).all()
                    
                    for emb in embeddings:
                        # Calculate cosine similarity
                        similarity = self._cosine_similarity(query_embedding, emb.vector)
                        
                        # Filter low similarity results
                        if similarity < 0.6:
                            continue
                        
                        # Get the content item
                        item = db.query(model_class).filter(model_class.id == emb.content_id).first()
                        if not item:
                            continue
                        
                        result = {
                            "id": item.id,
                            "type": content_type,
                            "score": float(similarity),  # Convert from numpy to Python float
                            "data": {}
                        }
                        
                        # Add fields based on content type
                        if content_type == "concept":
                            result["data"] = {
                                "name": item.name,
                                "description": item.description,
                                "examples": item.examples,
                                "is_verified": item.is_verified
                            }
                        elif content_type == "practice":
                            result["data"] = {
                                "name": item.name,
                                "description": item.description,
                                "implementation": item.implementation,
                                "benefits": item.benefits,
                                "is_verified": item.is_verified
                            }
                        elif content_type == "resource":
                            result["data"] = {
                                "title": item.title,
                                "type": item.content_type,
                                "description": item.description,
                                "url": item.url,
                                "is_verified": item.is_verified
                            }
                        elif content_type == "research":
                            result["data"] = {
                                "title": item.title,
                                "key_findings": item.key_findings,
                                "date": item.date_of_research,
                                "is_verified": item.is_verified
                            }
                        
                        results.append(result)
            
            # Sort by similarity score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:max_results]
        
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(v1)
        v2 = np.array(v2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return dot_product / (norm_v1 * norm_v2)
    
    def _combine_search_results(self, keyword_results: List[Dict[str, Any]], 
                              semantic_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine and rank results from keyword and semantic search"""
        # Build a map of existing results
        result_map = {}
        
        # First add keyword results
        for r in keyword_results:
            key = f"{r['type']}:{r['id']}"
            result_map[key] = r
        
        # Then add or update with semantic results
        for r in semantic_results:
            key = f"{r['type']}:{r['id']}"
            if key in result_map:
                # If the item exists in both, use the maximum score
                result_map[key]["score"] = max(result_map[key]["score"], r["score"])
            else:
                result_map[key] = r
        
        # Convert back to list and sort by score
        combined = list(result_map.values())
        combined.sort(key=lambda x: x["score"], reverse=True)
        
        return combined

# Create a singleton instance
_knowledge_base_instance = None

def get_enhanced_knowledge_base():
    """Get singleton instance of the enhanced knowledge base"""
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = EnhancedKnowledgeBase()
    return _knowledge_base_instance 