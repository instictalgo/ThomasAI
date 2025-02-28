import streamlit as st
import pandas as pd
from services.knowledge_base import GameDesignKnowledgeBase
import os
import logging
from ui.document_uploader import display_document_uploader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def display_knowledge_manager():
    """
    Display the knowledge management interface for game design knowledge.
    """
    st.title("Game Design Knowledge Manager")
    
    # Initialize knowledge base
    try:
        knowledge_base = GameDesignKnowledgeBase()
        st.success("Knowledge base connected successfully")
    except Exception as e:
        st.error(f"Error connecting to knowledge base: {str(e)}")
        logger.error(f"Error initializing knowledge base: {str(e)}")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Knowledge Manager")
    knowledge_section = st.sidebar.radio(
        "Select Section",
        ["Game Design Concepts", "Industry Practices", "Educational Resources", "Market Research", "Document Uploader"]
    )
    
    # Main content area
    if knowledge_section == "Game Design Concepts":
        display_game_design_concepts(knowledge_base)
    elif knowledge_section == "Industry Practices":
        display_industry_practices(knowledge_base)
    elif knowledge_section == "Educational Resources":
        display_educational_resources(knowledge_base)
    elif knowledge_section == "Market Research":
        display_market_research(knowledge_base)
    elif knowledge_section == "Document Uploader":
        display_document_uploader()

def display_game_design_concepts(knowledge_base):
    """Display and manage game design concepts."""
    st.header("Game Design Concepts")
    
    # Form for adding new concepts
    with st.expander("Add New Game Design Concept"):
        with st.form("add_concept_form"):
            concept_name = st.text_input("Concept Name")
            concept_description = st.text_area("Description")
            concept_examples = st.text_area("Examples")
            concept_references = st.text_area("References")
            
            submit_button = st.form_submit_button("Add Concept")
            
            if submit_button and concept_name and concept_description:
                try:
                    knowledge_base.add_design_concept(
                        concept_name,
                        concept_description,
                        concept_examples,
                        concept_references
                    )
                    st.success(f"Added concept: {concept_name}")
                    logger.info(f"Added game design concept: {concept_name}")
                except Exception as e:
                    st.error(f"Error adding concept: {str(e)}")
                    logger.error(f"Error adding game design concept: {str(e)}")
    
    # Search existing concepts
    st.subheader("Search Concepts")
    search_query = st.text_input("Search for concepts")
    
    if search_query:
        try:
            results = knowledge_base.search_knowledge_base(search_query, "game_design_concepts")
            if results:
                for result in results:
                    with st.expander(f"{result['name']}"):
                        st.write("**Description:**")
                        st.write(result['description'])
                        if result['examples']:
                            st.write("**Examples:**")
                            st.write(result['examples'])
                        if result['references']:
                            st.write("**References:**")
                            st.write(result['references'])
            else:
                st.info("No matching concepts found.")
        except Exception as e:
            st.error(f"Error searching concepts: {str(e)}")
            logger.error(f"Error searching game design concepts: {str(e)}")

def display_industry_practices(knowledge_base):
    """Display and manage industry practices."""
    st.header("Industry Practices")
    
    # Form for adding new practices
    with st.expander("Add New Industry Practice"):
        with st.form("add_practice_form"):
            practice_name = st.text_input("Practice Name")
            practice_description = st.text_area("Description")
            practice_companies = st.text_area("Companies Using This Practice")
            practice_outcomes = st.text_area("Outcomes and Benefits")
            
            submit_button = st.form_submit_button("Add Practice")
            
            if submit_button and practice_name and practice_description:
                try:
                    knowledge_base.add_industry_practice(
                        practice_name,
                        practice_description,
                        practice_companies,
                        practice_outcomes
                    )
                    st.success(f"Added practice: {practice_name}")
                    logger.info(f"Added industry practice: {practice_name}")
                except Exception as e:
                    st.error(f"Error adding practice: {str(e)}")
                    logger.error(f"Error adding industry practice: {str(e)}")
    
    # Search existing practices
    st.subheader("Search Practices")
    search_query = st.text_input("Search for industry practices")
    
    if search_query:
        try:
            results = knowledge_base.search_knowledge_base(search_query, "industry_practices")
            if results:
                for result in results:
                    with st.expander(f"{result['name']}"):
                        st.write("**Description:**")
                        st.write(result['description'])
                        if result['companies']:
                            st.write("**Companies:**")
                            st.write(result['companies'])
                        if result['outcomes']:
                            st.write("**Outcomes:**")
                            st.write(result['outcomes'])
            else:
                st.info("No matching practices found.")
        except Exception as e:
            st.error(f"Error searching practices: {str(e)}")
            logger.error(f"Error searching industry practices: {str(e)}")

def display_educational_resources(knowledge_base):
    """Display and manage educational resources."""
    st.header("Educational Resources")
    
    # Form for adding new resources
    with st.expander("Add New Educational Resource"):
        with st.form("add_resource_form"):
            resource_title = st.text_input("Resource Title")
            resource_type = st.selectbox("Resource Type", 
                                         ["Book", "Course", "Video", "Article", "Tool", "Other"])
            resource_url = st.text_input("URL/Link")
            resource_description = st.text_area("Description")
            resource_topics = st.text_area("Topics Covered")
            
            submit_button = st.form_submit_button("Add Resource")
            
            if submit_button and resource_title and resource_description:
                try:
                    knowledge_base.add_educational_resource(
                        resource_title,
                        resource_type,
                        resource_url,
                        resource_description,
                        resource_topics
                    )
                    st.success(f"Added resource: {resource_title}")
                    logger.info(f"Added educational resource: {resource_title}")
                except Exception as e:
                    st.error(f"Error adding resource: {str(e)}")
                    logger.error(f"Error adding educational resource: {str(e)}")
    
    # Search existing resources
    st.subheader("Search Resources")
    search_query = st.text_input("Search for educational resources")
    
    if search_query:
        try:
            results = knowledge_base.search_knowledge_base(search_query, "educational_resources")
            if results:
                for result in results:
                    with st.expander(f"{result['title']} ({result['type']})"):
                        st.write("**Description:**")
                        st.write(result['description'])
                        if result['url']:
                            st.write("**URL:**")
                            st.markdown(f"[{result['url']}]({result['url']})")
                        if result['topics']:
                            st.write("**Topics:**")
                            st.write(result['topics'])
            else:
                st.info("No matching resources found.")
        except Exception as e:
            st.error(f"Error searching resources: {str(e)}")
            logger.error(f"Error searching educational resources: {str(e)}")

def display_market_research(knowledge_base):
    """Display and manage market research."""
    st.header("Market Research")
    
    # Form for adding new research
    with st.expander("Add New Market Research"):
        with st.form("add_research_form"):
            research_title = st.text_input("Research Title")
            research_date = st.date_input("Research Date")
            research_source = st.text_input("Source")
            research_findings = st.text_area("Key Findings")
            research_implications = st.text_area("Implications for Game Development")
            
            submit_button = st.form_submit_button("Add Research")
            
            if submit_button and research_title and research_findings:
                try:
                    knowledge_base.add_market_research(
                        research_title,
                        research_date.strftime("%Y-%m-%d"),
                        research_source,
                        research_findings,
                        research_implications
                    )
                    st.success(f"Added research: {research_title}")
                    logger.info(f"Added market research: {research_title}")
                except Exception as e:
                    st.error(f"Error adding research: {str(e)}")
                    logger.error(f"Error adding market research: {str(e)}")
    
    # Search existing research
    st.subheader("Search Market Research")
    search_query = st.text_input("Search for market research")
    
    if search_query:
        try:
            results = knowledge_base.search_knowledge_base(search_query, "market_research")
            if results:
                for result in results:
                    with st.expander(f"{result['title']} ({result['date']})"):
                        if result['source']:
                            st.write(f"**Source:** {result['source']}")
                        st.write("**Key Findings:**")
                        st.write(result['findings'])
                        if result['implications']:
                            st.write("**Implications:**")
                            st.write(result['implications'])
            else:
                st.info("No matching research found.")
        except Exception as e:
            st.error(f"Error searching research: {str(e)}")
            logger.error(f"Error searching market research: {str(e)}")

if __name__ == "__main__":
    display_knowledge_manager() 