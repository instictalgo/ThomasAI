import os
import sqlite3
import json
import requests
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("knowledge_base")

class GameDesignKnowledgeBase:
    """
    Knowledge base for game design concepts, industry practices, and educational materials.
    This class manages the storing, retrieving, and integrating of game design knowledge 
    to enhance Thomas AI's capabilities.
    """
    
    def __init__(self, db_path="knowledge_base.db"):
        """Initialize the knowledge base with the database path"""
        self.db_path = db_path
        self.ensure_db_exists()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    def ensure_db_exists(self):
        """Create the database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for different knowledge types
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_design_concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            examples TEXT,
            category TEXT,
            tags TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS industry_practices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            practice_name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            implementation TEXT,
            benefits TEXT,
            challenges TEXT,
            case_studies TEXT,
            category TEXT,
            tags TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS educational_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content_type TEXT NOT NULL,
            description TEXT NOT NULL,
            url TEXT,
            author TEXT,
            publication_date TEXT,
            summary TEXT,
            key_points TEXT,
            category TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            game_genre TEXT,
            platform TEXT,
            target_audience TEXT,
            key_findings TEXT NOT NULL,
            metrics TEXT,
            trends TEXT,
            date_of_research TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            embedding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def add_design_concept(self, concept_data):
        """
        Add a new game design concept to the knowledge base
        
        Args:
            concept_data (dict): Data about the game design concept
        
        Returns:
            int: ID of the newly added concept
        """
        required_fields = ["concept_name", "description"]
        for field in required_fields:
            if field not in concept_data:
                raise ValueError(f"Missing required field: {field}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert any list or dict fields to JSON strings
        for key, value in concept_data.items():
            if isinstance(value, (list, dict)):
                concept_data[key] = json.dumps(value)
        
        # Prepare fields and values for SQL
        fields = list(concept_data.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = [concept_data[field] for field in fields]
        
        # Handle potential duplicates
        try:
            query = f"INSERT INTO game_design_concepts ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            concept_id = cursor.lastrowid
            
            # Create embedding for this concept for semantic search
            if self.openai_api_key:
                self._create_embedding(concept_id, "game_design_concepts", concept_data)
            
            conn.commit()
            logger.info(f"Added design concept: {concept_data['concept_name']}")
            return concept_id
        except sqlite3.IntegrityError:
            # Update if the concept already exists
            set_clause = ", ".join([f"{field} = ?" for field in fields])
            update_values = values + [concept_data["concept_name"]]
            
            query = f"UPDATE game_design_concepts SET {set_clause} WHERE concept_name = ?"
            cursor.execute(query, update_values)
            
            # Get the ID of the updated concept
            cursor.execute("SELECT id FROM game_design_concepts WHERE concept_name = ?", (concept_data["concept_name"],))
            concept_id = cursor.fetchone()[0]
            
            # Update the embedding
            if self.openai_api_key:
                self._update_embedding(concept_id, "game_design_concepts", concept_data)
            
            conn.commit()
            logger.info(f"Updated design concept: {concept_data['concept_name']}")
            return concept_id
        finally:
            conn.close()
    
    def add_industry_practice(self, practice_data):
        """
        Add a new industry practice to the knowledge base
        
        Args:
            practice_data (dict): Data about the industry practice
        
        Returns:
            int: ID of the newly added practice
        """
        required_fields = ["practice_name", "description"]
        for field in required_fields:
            if field not in practice_data:
                raise ValueError(f"Missing required field: {field}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert any list or dict fields to JSON strings
        for key, value in practice_data.items():
            if isinstance(value, (list, dict)):
                practice_data[key] = json.dumps(value)
        
        # Prepare fields and values for SQL
        fields = list(practice_data.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = [practice_data[field] for field in fields]
        
        # Handle potential duplicates
        try:
            query = f"INSERT INTO industry_practices ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            practice_id = cursor.lastrowid
            
            # Create embedding for this practice
            if self.openai_api_key:
                self._create_embedding(practice_id, "industry_practices", practice_data)
            
            conn.commit()
            logger.info(f"Added industry practice: {practice_data['practice_name']}")
            return practice_id
        except sqlite3.IntegrityError:
            # Update if the practice already exists
            set_clause = ", ".join([f"{field} = ?" for field in fields])
            update_values = values + [practice_data["practice_name"]]
            
            query = f"UPDATE industry_practices SET {set_clause} WHERE practice_name = ?"
            cursor.execute(query, update_values)
            
            # Get the ID of the updated practice
            cursor.execute("SELECT id FROM industry_practices WHERE practice_name = ?", (practice_data["practice_name"],))
            practice_id = cursor.fetchone()[0]
            
            # Update the embedding
            if self.openai_api_key:
                self._update_embedding(practice_id, "industry_practices", practice_data)
            
            conn.commit()
            logger.info(f"Updated industry practice: {practice_data['practice_name']}")
            return practice_id
        finally:
            conn.close()
    
    def add_educational_resource(self, resource_data):
        """
        Add a new educational resource to the knowledge base
        
        Args:
            resource_data (dict): Data about the educational resource
        
        Returns:
            int: ID of the newly added resource
        """
        required_fields = ["title", "content_type", "description"]
        for field in required_fields:
            if field not in resource_data:
                raise ValueError(f"Missing required field: {field}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert any list or dict fields to JSON strings
        for key, value in resource_data.items():
            if isinstance(value, (list, dict)):
                resource_data[key] = json.dumps(value)
        
        # Prepare fields and values for SQL
        fields = list(resource_data.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = [resource_data[field] for field in fields]
        
        # Handle potential duplicates
        try:
            query = f"INSERT INTO educational_resources ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            resource_id = cursor.lastrowid
            
            # Create embedding for this resource
            if self.openai_api_key:
                self._create_embedding(resource_id, "educational_resources", resource_data)
            
            conn.commit()
            logger.info(f"Added educational resource: {resource_data['title']}")
            return resource_id
        except sqlite3.IntegrityError:
            # Update if the resource already exists
            set_clause = ", ".join([f"{field} = ?" for field in fields])
            update_values = values + [resource_data["title"]]
            
            query = f"UPDATE educational_resources SET {set_clause} WHERE title = ?"
            cursor.execute(query, update_values)
            
            # Get the ID of the updated resource
            cursor.execute("SELECT id FROM educational_resources WHERE title = ?", (resource_data["title"],))
            resource_id = cursor.fetchone()[0]
            
            # Update the embedding
            if self.openai_api_key:
                self._update_embedding(resource_id, "educational_resources", resource_data)
            
            conn.commit()
            logger.info(f"Updated educational resource: {resource_data['title']}")
            return resource_id
        finally:
            conn.close()
    
    def add_market_research(self, research_data):
        """
        Add new market research to the knowledge base
        
        Args:
            research_data (dict): Data about the market research
        
        Returns:
            int: ID of the newly added research
        """
        required_fields = ["title", "key_findings"]
        for field in required_fields:
            if field not in research_data:
                raise ValueError(f"Missing required field: {field}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert any list or dict fields to JSON strings
        for key, value in research_data.items():
            if isinstance(value, (list, dict)):
                research_data[key] = json.dumps(value)
        
        # Prepare fields and values for SQL
        fields = list(research_data.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = [research_data[field] for field in fields]
        
        # Add the research
        query = f"INSERT INTO market_research ({', '.join(fields)}) VALUES ({placeholders})"
        cursor.execute(query, values)
        research_id = cursor.lastrowid
        
        # Create embedding for this research
        if self.openai_api_key:
            self._create_embedding(research_id, "market_research", research_data)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Added market research: {research_data['title']}")
        return research_id
    
    def search_knowledge_base(self, query, category=None, limit=5):
        """
        Search the knowledge base for relevant information
        
        Args:
            query (str): The search query
            category (str, optional): Specific category to search in
            limit (int, optional): Maximum number of results to return
        
        Returns:
            list: List of matching results
        """
        if self.openai_api_key and len(query) > 10:
            # Use semantic search if query is substantial
            return self._semantic_search(query, category, limit)
        else:
            # Fall back to keyword search
            return self._keyword_search(query, category, limit)
    
    def _keyword_search(self, query, category=None, limit=5):
        """
        Perform a keyword-based search in the knowledge base
        
        Args:
            query (str): The search query
            category (str, optional): Specific category to search in
            limit (int, optional): Maximum number of results to return
        
        Returns:
            list: List of matching results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = []
        search_terms = f"%{query}%"
        
        # Define tables to search based on category
        tables = {
            "game_design_concepts": ["concept_name", "description", "examples", "category", "tags"],
            "industry_practices": ["practice_name", "description", "implementation", "benefits", "challenges", "case_studies", "category", "tags"],
            "educational_resources": ["title", "description", "summary", "key_points", "category", "tags"],
            "market_research": ["title", "game_genre", "platform", "target_audience", "key_findings", "metrics", "trends"]
        }
        
        # If category specified, only search that table
        if category and category in tables:
            tables_to_search = {category: tables[category]}
        else:
            tables_to_search = tables
        
        # Search each table
        for table, fields in tables_to_search.items():
            conditions = " OR ".join([f"{field} LIKE ?" for field in fields])
            params = [search_terms] * len(fields)
            
            query_sql = f"SELECT *, '{table}' as source_table FROM {table} WHERE {conditions} LIMIT {limit}"
            cursor.execute(query_sql, params)
            
            for row in cursor.fetchall():
                result = dict(row)
                results.append(result)
        
        conn.close()
        return results[:limit]
    
    def _create_embedding(self, content_id, content_type, content_data):
        """
        Create an embedding for a piece of content using OpenAI's API
        
        Args:
            content_id (int): ID of the content
            content_type (str): Type of content
            content_data (dict): Content data
        """
        try:
            # Prepare the text to embed
            text_to_embed = ""
            if content_type == "game_design_concepts":
                text_to_embed = f"{content_data['concept_name']}: {content_data['description']} {content_data.get('examples', '')}"
            elif content_type == "industry_practices":
                text_to_embed = f"{content_data['practice_name']}: {content_data['description']} {content_data.get('implementation', '')} {content_data.get('benefits', '')}"
            elif content_type == "educational_resources":
                text_to_embed = f"{content_data['title']}: {content_data['description']} {content_data.get('summary', '')} {content_data.get('key_points', '')}"
            elif content_type == "market_research":
                text_to_embed = f"{content_data['title']}: {content_data.get('game_genre', '')} {content_data.get('platform', '')} {content_data['key_findings']} {content_data.get('trends', '')}"
            
            # Get embedding from OpenAI
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": text_to_embed,
                "model": "text-embedding-ada-002"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                embedding = response.json()["data"][0]["embedding"]
                
                # Store embedding in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO embeddings (content_id, content_type, embedding) VALUES (?, ?, ?)",
                    (content_id, content_type, json.dumps(embedding))
                )
                
                conn.commit()
                conn.close()
                logger.info(f"Created embedding for {content_type} with ID {content_id}")
            else:
                logger.error(f"Failed to create embedding: {response.text}")
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
    
    def _update_embedding(self, content_id, content_type, content_data):
        """
        Update the embedding for a piece of content
        
        Args:
            content_id (int): ID of the content
            content_type (str): Type of content
            content_data (dict): Content data
        """
        try:
            # Delete old embedding
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM embeddings WHERE content_id = ? AND content_type = ?",
                (content_id, content_type)
            )
            
            conn.commit()
            conn.close()
            
            # Create new embedding
            self._create_embedding(content_id, content_type, content_data)
            logger.info(f"Updated embedding for {content_type} with ID {content_id}")
        except Exception as e:
            logger.error(f"Error updating embedding: {str(e)}")
    
    def _semantic_search(self, query, category=None, limit=5):
        """
        Perform a semantic search using embeddings
        
        Args:
            query (str): The search query
            category (str, optional): Specific category to search in
            limit (int, optional): Maximum number of results to return
        
        Returns:
            list: List of matching results
        """
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
                logger.error(f"Failed to get query embedding: {response.text}")
                return self._keyword_search(query, category, limit)
            
            query_embedding = response.json()["data"][0]["embedding"]
            
            # Load all embeddings
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query based on category
            if category:
                cursor.execute(
                    "SELECT * FROM embeddings WHERE content_type = ?",
                    (category,)
                )
            else:
                cursor.execute("SELECT * FROM embeddings")
            
            embeddings = cursor.fetchall()
            
            # Calculate cosine similarity
            import numpy as np
            from scipy.spatial.distance import cosine
            
            similarities = []
            for emb in embeddings:
                content_id = emb["content_id"]
                content_type = emb["content_type"]
                embedding = np.array(json.loads(emb["embedding"]))
                
                # Calculate similarity
                similarity = 1 - cosine(query_embedding, embedding)
                similarities.append((content_id, content_type, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[2], reverse=True)
            
            # Get top results
            results = []
            for content_id, content_type, similarity in similarities[:limit]:
                # Fetch the content
                cursor.execute(f"SELECT * FROM {content_type} WHERE id = ?", (content_id,))
                content = dict(cursor.fetchone())
                content["relevance_score"] = similarity
                content["source_table"] = content_type
                results.append(content)
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return self._keyword_search(query, category, limit)
    
    def get_knowledge_for_context(self, query, limit=3):
        """
        Get knowledge to provide context for Thomas AI based on a query
        
        Args:
            query (str): The user's query
            limit (int, optional): Maximum number of results to include
        
        Returns:
            str: Formatted knowledge for context
        """
        results = self.search_knowledge_base(query, limit=limit)
        
        if not results:
            return ""
        
        # Format results into a context string
        context = "Here's some relevant information from my knowledge base:\n\n"
        
        for result in results:
            source_table = result.get("source_table", "unknown")
            
            if source_table == "game_design_concepts":
                context += f"## Game Design Concept: {result.get('concept_name', 'Unnamed')}\n"
                context += f"{result.get('description', '')}\n"
                if 'examples' in result and result['examples']:
                    examples = result['examples']
                    if isinstance(examples, str) and examples.startswith("["):
                        try:
                            examples = json.loads(examples)
                            context += "Examples:\n"
                            for example in examples:
                                context += f"- {example}\n"
                        except:
                            context += f"Examples: {examples}\n"
                    else:
                        context += f"Examples: {examples}\n"
                context += "\n"
            
            elif source_table == "industry_practices":
                context += f"## Industry Practice: {result.get('practice_name', 'Unnamed')}\n"
                context += f"{result.get('description', '')}\n"
                if 'benefits' in result and result['benefits']:
                    context += f"Benefits: {result.get('benefits', '')}\n"
                if 'challenges' in result and result['challenges']:
                    context += f"Challenges: {result.get('challenges', '')}\n"
                context += "\n"
            
            elif source_table == "educational_resources":
                context += f"## Educational Resource: {result.get('title', 'Unnamed')}\n"
                context += f"Type: {result.get('content_type', 'Unknown')}\n"
                context += f"{result.get('description', '')}\n"
                if 'key_points' in result and result['key_points']:
                    key_points = result['key_points']
                    if isinstance(key_points, str) and key_points.startswith("["):
                        try:
                            key_points = json.loads(key_points)
                            context += "Key Points:\n"
                            for point in key_points:
                                context += f"- {point}\n"
                        except:
                            context += f"Key Points: {key_points}\n"
                    else:
                        context += f"Key Points: {key_points}\n"
                context += "\n"
            
            elif source_table == "market_research":
                context += f"## Market Research: {result.get('title', 'Unnamed')}\n"
                if 'game_genre' in result and result['game_genre']:
                    context += f"Genre: {result.get('game_genre', '')}\n"
                if 'platform' in result and result['platform']:
                    context += f"Platform: {result.get('platform', '')}\n"
                context += f"Key Findings: {result.get('key_findings', '')}\n"
                if 'trends' in result and result['trends']:
                    context += f"Trends: {result.get('trends', '')}\n"
                context += "\n"
        
        return context
    
    def initialize_with_sample_data(self):
        """Initialize the knowledge base with sample game design concepts"""
        # Game Design Concepts
        concepts = [
            {
                "concept_name": "Core Game Loop",
                "description": "The central, repeatable activity that players engage with in a game. It defines the main gameplay experience and is typically the most refined and polished aspect of the game.",
                "examples": json.dumps([
                    "In Tetris, the core loop is rotating and placing falling blocks to clear lines",
                    "In first-person shooters, the core loop is moving, aiming, and shooting",
                    "In match-3 games, the core loop is swapping adjacent tiles to create matches"
                ]),
                "category": "Game Design Fundamentals",
                "tags": "gameplay, mechanics, design"
            },
            {
                "concept_name": "Player Retention",
                "description": "The ability of a game to keep players engaged and returning over time. Strong retention is crucial for live service and free-to-play games' success.",
                "examples": json.dumps([
                    "Daily login rewards in mobile games",
                    "Season passes in battle royale games",
                    "Weekly challenges in live service games"
                ]),
                "category": "Monetization",
                "tags": "metrics, engagement, monetization"
            },
            {
                "concept_name": "Game Balance",
                "description": "The practice of tuning a game's systems and mechanics to ensure fair, engaging gameplay without dominant strategies or unintended advantages.",
                "examples": json.dumps([
                    "Balancing character abilities in MOBAs",
                    "Weapon statistics in shooters",
                    "Resource generation rates in strategy games"
                ]),
                "category": "Game Design Fundamentals",
                "tags": "mechanics, tuning, design"
            }
        ]
        
        for concept in concepts:
            self.add_design_concept(concept)
        
        # Industry Practices
        practices = [
            {
                "practice_name": "Agile Game Development",
                "description": "An iterative approach to game development that emphasizes flexibility, continuous testing, and regular deliverables.",
                "implementation": "Typically implemented using Scrum or Kanban methodologies with 2-4 week sprints.",
                "benefits": "Faster iteration, better risk management, more responsive to player feedback.",
                "challenges": "Difficulty in estimating completion dates, potential scope creep, requires strong team coordination.",
                "case_studies": json.dumps([
                    "Ubisoft's transition to Agile for Assassin's Creed franchise",
                    "How Bungie uses Agile for Destiny's live service model"
                ]),
                "category": "Project Management",
                "tags": "development, methodology, production"
            },
            {
                "practice_name": "Minimum Viable Product (MVP) Approach",
                "description": "Creating a version of a game with just enough features to be playable and test core assumptions before investing in full production.",
                "implementation": "Start with core gameplay loop only, focus on what makes the game unique, eliminate all non-essential features.",
                "benefits": "Reduces initial development costs, allows for early player feedback, identifies design issues early.",
                "challenges": "Difficult to determine what's truly 'minimum', players may judge harshly if too limited.",
                "category": "Project Management",
                "tags": "development, production, prototyping"
            }
        ]
        
        for practice in practices:
            self.add_industry_practice(practice)
        
        # Educational Resources
        resources = [
            {
                "title": "The Art of Game Design: A Book of Lenses",
                "content_type": "Book",
                "description": "A comprehensive guide to game design by Jesse Schell that provides multiple perspectives or 'lenses' through which to view and improve game designs.",
                "author": "Jesse Schell",
                "publication_date": "2008",
                "key_points": json.dumps([
                    "100+ 'lenses' for analyzing game design",
                    "Focus on player experience over mechanics",
                    "Balance between analytical and creative approaches",
                    "Universal principles applicable to all game types"
                ]),
                "category": "Game Design",
                "tags": "design, fundamentals, theory"
            },
            {
                "title": "GDC Game Design Workshop: Balancing Competitive Multiplayer Games",
                "content_type": "Conference Talk",
                "description": "Game Developers Conference presentation on techniques for balancing competitive games to ensure fairness and strategic depth.",
                "url": "https://www.gdcvault.com/",
                "author": "Various Industry Experts",
                "key_points": json.dumps([
                    "Asymmetric vs. symmetric balance approaches",
                    "Data-driven balance methodologies",
                    "Community feedback integration techniques",
                    "Common balance pitfalls and how to avoid them"
                ]),
                "category": "Game Balance",
                "tags": "multiplayer, competitive, balance"
            }
        ]
        
        for resource in resources:
            self.add_educational_resource(resource)
        
        # Market Research
        research = [
            {
                "title": "Mobile Gaming Trends 2023",
                "game_genre": "Multiple",
                "platform": "Mobile",
                "target_audience": "Casual and mid-core players",
                "key_findings": "Hybrid-casual games are seeing strong growth, combining casual mechanics with deeper progression systems. Battle passes continue to outperform traditional gacha mechanics in terms of player satisfaction.",
                "metrics": json.dumps({
                    "average_revenue_per_daily_active_user": "$0.58",
                    "day_1_retention_benchmark": "35%",
                    "day_30_retention_benchmark": "8%"
                }),
                "trends": "Shift towards more accessible midcore experiences, rise of alternative app stores, increasing importance of IP-based games",
                "date_of_research": "2023-01-15",
                "source": "Industry Report"
            },
            {
                "title": "Player Motivations in Battle Royale Games",
                "game_genre": "Battle Royale",
                "platform": "Cross-platform",
                "target_audience": "Competitive players aged 16-34",
                "key_findings": "The primary appeal for most players is not winning but the 'high tension moments' created by the shrinking playspace and unexpected encounters. Social features are increasingly important for retention.",
                "metrics": json.dumps({
                    "average_session_length": "22 minutes",
                    "matches_per_day_per_active_user": "4.7",
                    "cosmetic_conversion_rate": "12%"
                }),
                "trends": "Integration with social platforms, emphasis on squad-based play, expansion of non-combat activities within games",
                "date_of_research": "2022-09-30",
                "source": "Player Motivation Study"
            }
        ]
        
        for research_item in research:
            self.add_market_research(research_item)
        
        logger.info("Knowledge base initialized with sample data")


# Helper function to get the knowledge base instance
_knowledge_base_instance = None

def get_knowledge_base():
    """Get the singleton instance of the knowledge base"""
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = GameDesignKnowledgeBase()
    return _knowledge_base_instance 