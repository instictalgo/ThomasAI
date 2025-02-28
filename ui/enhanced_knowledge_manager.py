import streamlit as st
import pandas as pd
import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from ui.components.knowledge_graph import taxonomy_tree_visualization, concept_relationships_visualization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_knowledge_manager")

# API Base URL
API_BASE_URL = "http://localhost:8002"

# Cache TTL in seconds
CACHE_TTL = 300
_cache = {}

def get_from_cache(key, default=None):
    """Get a value from the cache if it's not expired."""
    if key in _cache:
        timestamp, value = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
    return default

def set_in_cache(key, value):
    """Set a value in the cache with current timestamp."""
    _cache[key] = (time.time(), value)
    return value

def api_get(endpoint, params=None, use_cache=True):
    """Get data from the API with caching."""
    cache_key = f"get:{endpoint}:{json.dumps(params) if params else ''}"
    
    # Check cache first
    if use_cache:
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
    
    # Make API request
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if use_cache:
                set_in_cache(cache_key, data)
            return data
        else:
            logger.error(f"API request to {endpoint} failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"API request to {endpoint} failed: {str(e)}")
        return None

def api_post(endpoint, data, use_cache=False):
    """Post data to the API."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code in (200, 201):
            result = response.json()
            
            # Clear cache for GET endpoints related to this resource
            if endpoint.startswith("/v2/knowledge"):
                for key in list(_cache.keys()):
                    if key.startswith("get:/v2/knowledge"):
                        del _cache[key]
            
            return result
        else:
            logger.error(f"API request to {endpoint} failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"API request to {endpoint} failed: {str(e)}")
        return None

def display_enhanced_knowledge_manager():
    """Display the enhanced knowledge management interface."""
    st.title("Enhanced Knowledge Management")
    
    # Check if API is available
    health = api_get("/health", use_cache=False)
    if not health or health.get("status") != "healthy":
        st.error("Cannot connect to the API. Please make sure the API server is running.")
        st.error(f"API Health: {health}")
        return
    
    # Use tabs for main sections
    tabs = st.tabs(["Overview", "Taxonomy", "Concepts", "Practices", "Resources", "Research", "Search"])
    
    with tabs[0]:
        display_overview()
    
    with tabs[1]:
        display_taxonomy_manager()
    
    with tabs[2]:
        display_concepts_manager()
    
    with tabs[3]:
        display_practices_manager()
    
    with tabs[4]:
        display_resources_manager()
    
    with tabs[5]:
        display_research_manager()
    
    with tabs[6]:
        display_search_interface()

def display_overview():
    """Display overview of the knowledge base."""
    st.header("Knowledge Base Overview")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # TODO: Get actual counts from API
        st.metric("Game Design Concepts", "42")
    
    with col2:
        st.metric("Industry Practices", "38")
    
    with col3:
        st.metric("Educational Resources", "25")
    
    with col4:
        st.metric("Market Research", "17")
    
    # Display recent activity
    st.subheader("Recent Activity")
    
    # TODO: Get actual activity from API
    # For now, use mock data
    recent_activity = [
        {"type": "concept", "action": "created", "name": "Progression Systems", "user": "admin", "timestamp": "2023-05-10T14:23:45"},
        {"type": "practice", "action": "updated", "name": "Agile Game Development", "user": "john_doe", "timestamp": "2023-05-09T16:12:30"},
        {"type": "resource", "action": "verified", "name": "Game Design Patterns", "user": "reviewer1", "timestamp": "2023-05-08T09:45:22"},
        {"type": "research", "action": "created", "name": "Mobile Gaming Trends 2023", "user": "analyst", "timestamp": "2023-05-07T11:34:12"},
        {"type": "concept", "action": "relationship_added", "name": "Game Loops", "related_to": "Progression Systems", "user": "admin", "timestamp": "2023-05-06T15:22:10"}
    ]
    
    activity_df = pd.DataFrame(recent_activity)
    st.dataframe(activity_df)
    
    # Display visualization
    st.subheader("Knowledge Graph")
    
    # TODO: Get actual data from API
    # For now, use mock data for visualization
    nodes = [
        {"id": 1, "label": "Game Loops", "description": "Core repeatable activities", "level": 1},
        {"id": 2, "label": "Progression Systems", "description": "How players advance", "level": 1},
        {"id": 3, "label": "Monetization", "description": "Revenue generation", "level": 1},
        {"id": 4, "label": "F2P", "description": "Free to play model", "level": 2},
        {"id": 5, "label": "Premium", "description": "Paid upfront model", "level": 2},
        {"id": 6, "label": "XP Systems", "description": "Experience point based progression", "level": 2},
        {"id": 7, "label": "Core Loop", "description": "Main gameplay loop", "level": 2}
    ]
    
    edges = [
        {"source": 1, "target": 7, "label": "has_subtype"},
        {"source": 2, "target": 6, "label": "has_example"},
        {"source": 3, "target": 4, "label": "has_subtype"},
        {"source": 3, "target": 5, "label": "has_subtype"},
        {"source": 1, "target": 2, "label": "relates_to"},
        {"source": 3, "target": 2, "label": "can_influence"}
    ]
    
    from ui.components.knowledge_graph import knowledge_graph
    knowledge_graph(nodes, edges, title="Knowledge Graph Overview", height=400)

def display_taxonomy_manager():
    """Display the taxonomy management interface."""
    st.header("Taxonomy Management")
    
    # Get taxonomy tree from API
    taxonomy_tree = api_get("/v2/knowledge/taxonomy")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Form to create a new taxonomy node
        with st.form("create_taxonomy_form"):
            st.subheader("Create New Taxonomy Node")
            
            name = st.text_input("Name")
            description = st.text_area("Description")
            
            # Get existing taxonomy nodes for parent selection
            all_nodes = []
            if taxonomy_tree:
                def extract_nodes(nodes):
                    result = []
                    for node in nodes:
                        result.append((node['id'], node['name']))
                        if 'children' in node and node['children']:
                            result.extend(extract_nodes(node['children']))
                    return result
                
                all_nodes = extract_nodes(taxonomy_tree)
            
            parent_options = [("None", "No Parent (Root Node)")] + all_nodes
            parent_selection = st.selectbox(
                "Parent Node", 
                options=[opt[0] for opt in parent_options],
                format_func=lambda x: next((opt[1] for opt in parent_options if opt[0] == x), str(x))
            )
            
            parent_id = None if parent_selection == "None" else parent_selection
            
            submit = st.form_submit_button("Create Taxonomy Node")
            
            if submit:
                if name:
                    # Create the taxonomy node
                    response = api_post("/v2/knowledge/taxonomy", {
                        "name": name,
                        "description": description,
                        "parent_id": parent_id
                    })
                    
                    if response:
                        st.success(f"Created taxonomy node: {name}")
                        # Clear cache to refresh the taxonomy tree
                        if "get:/v2/knowledge/taxonomy" in _cache:
                            del _cache["get:/v2/knowledge/taxonomy"]
                        # Rerun to refresh the page
                        st.experimental_rerun()
                    else:
                        st.error("Failed to create taxonomy node")
                else:
                    st.warning("Please enter a name for the taxonomy node")
    
    with col2:
        # Display the taxonomy tree
        st.subheader("Taxonomy Tree")
        
        if taxonomy_tree:
            # Visualization using the knowledge graph component
            taxonomy_tree_visualization(taxonomy_tree, title="Taxonomy Hierarchy", height=600)
            
            # Expandable tree view
            st.subheader("Tree View")
            
            def display_node(node, depth=0):
                expanded = depth < 2  # Auto-expand first two levels
                with st.expander(f"{node['name']}", expanded=expanded):
                    st.write(f"**Description:** {node.get('description', 'No description')}")
                    st.write(f"**Level:** {node.get('level', 0)}")
                    st.write(f"**ID:** {node['id']}")
                    
                    # Display edit/delete buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit", key=f"edit_{node['id']}"):
                            st.session_state.edit_taxonomy_node = node
                    with col2:
                        if st.button(f"Delete", key=f"delete_{node['id']}"):
                            # TODO: Implement deletion (would require API endpoint)
                            st.warning("Deletion not implemented yet")
                    
                    # Display children
                    if 'children' in node and node['children']:
                        for child in node['children']:
                            display_node(child, depth + 1)
            
            for node in taxonomy_tree:
                display_node(node)
        else:
            st.info("No taxonomy nodes found. Create some using the form on the left.")

def display_concepts_manager():
    """Display the game design concepts management interface."""
    st.header("Game Design Concepts")
    
    # TODO: Create a proper interface
    st.info("This section is under construction.")
    
    # Placeholder for concept management interface
    with st.expander("Add New Concept"):
        with st.form("add_concept_form"):
            st.text_input("Name")
            st.text_area("Description")
            st.text_area("Examples")
            st.text_area("References")
            
            # Taxonomy selection
            st.multiselect("Taxonomies", options=[])
            
            st.form_submit_button("Add Concept")
    
    # Concept relationships visualization placeholder
    st.subheader("Concept Relationships")
    
    # Mock data for concept relationships visualization
    concepts = [
        {"id": 1, "name": "Core Loop", "description": "Central repeatable gameplay activity", "is_verified": True},
        {"id": 2, "name": "Meta Game", "description": "Systems outside core gameplay", "is_verified": True},
        {"id": 3, "name": "Progression", "description": "How players advance", "is_verified": True},
        {"id": 4, "name": "Engagement Loop", "description": "Motivates player return", "is_verified": False}
    ]
    
    relationships = [
        {"source_id": 1, "target_id": 2, "relationship_type": "complements", "strength": 0.8},
        {"source_id": 2, "target_id": 3, "relationship_type": "includes", "strength": 0.9},
        {"source_id": 3, "target_id": 4, "relationship_type": "drives", "strength": 0.7},
        {"source_id": 1, "target_id": 4, "relationship_type": "feeds", "strength": 0.6}
    ]
    
    concept_relationships_visualization(concepts, relationships)

def display_practices_manager():
    """Display the industry practices management interface."""
    st.header("Industry Practices")
    
    # TODO: Create a proper interface
    st.info("This section is under construction.")

def display_resources_manager():
    """Display the educational resources management interface."""
    st.header("Educational Resources")
    
    # TODO: Create a proper interface
    st.info("This section is under construction.")

def display_research_manager():
    """Display the market research management interface."""
    st.header("Market Research")
    
    # TODO: Create a proper interface
    st.info("This section is under construction.")

def display_search_interface():
    """Display the search interface."""
    st.header("Knowledge Base Search")
    
    # Search form
    query = st.text_input("Search Query")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        content_types = st.multiselect(
            "Content Types",
            options=["concept", "practice", "resource", "research"],
            default=["concept", "practice", "resource", "research"]
        )
    
    with col2:
        use_semantic = st.checkbox("Use Semantic Search", value=True)
        max_results = st.slider("Max Results", min_value=5, max_value=50, value=10)
    
    if query:
        # Perform the search
        search_params = {
            "query": query,
            "content_types": content_types,
            "max_results": max_results,
            "use_semantic": use_semantic
        }
        
        with st.spinner("Searching..."):
            results = api_post("/v2/knowledge/search", search_params)
        
        if results and "results" in results:
            st.success(f"Found {len(results['results'])} results")
            
            # Group results by type
            grouped_results = {}
            for result in results["results"]:
                result_type = result["type"]
                if result_type not in grouped_results:
                    grouped_results[result_type] = []
                grouped_results[result_type].append(result)
            
            # Display results by type in tabs
            if grouped_results:
                result_tabs = st.tabs(list(grouped_results.keys()))
                
                for i, (result_type, type_results) in enumerate(grouped_results.items()):
                    with result_tabs[i]:
                        for j, result in enumerate(type_results):
                            score = result.get("score", 0)
                            with st.expander(f"{j+1}. {_get_result_title(result)} (Score: {score:.2f})"):
                                st.json(result["data"])
            else:
                st.info("No results found.")
        else:
            st.warning("No results found or search failed.")

def _get_result_title(result):
    """Get a title for a search result based on its type."""
    result_type = result["type"]
    data = result["data"]
    
    if result_type == "concept":
        return data.get("name", "Unnamed Concept")
    elif result_type == "practice":
        return data.get("name", "Unnamed Practice")
    elif result_type == "resource":
        return data.get("title", "Unnamed Resource")
    elif result_type == "research":
        return data.get("title", "Unnamed Research")
    else:
        return "Unknown Result"

if __name__ == "__main__":
    display_enhanced_knowledge_manager() 