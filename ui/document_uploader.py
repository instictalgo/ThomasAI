import streamlit as st
import os
import tempfile
import logging
import pandas as pd
import PyPDF2
import docx
import json
import requests
from services.knowledge_base import GameDesignKnowledgeBase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {str(e)}")
        return ""

def analyze_text_with_openai(text, api_key, document_type):
    """
    Analyze document text with OpenAI to extract game design knowledge.
    
    Args:
        text (str): The text to analyze
        api_key (str): OpenAI API key
        document_type (str): Type of document (GDD, Concept, Research, etc.)
        
    Returns:
        dict: Extracted knowledge categorized by type
    """
    if not api_key:
        logger.error("No OpenAI API key provided")
        return None
        
    # Prepare the prompt based on document type
    if document_type == "Game Design Document":
        prompt = """
        Extract the following information from this Game Design Document:
        1. Game design concepts and mechanics
        2. Industry practices mentioned
        3. Educational resources referenced
        4. Market research insights
        
        Format your response as a JSON object with these keys:
        {
            "design_concepts": [{"name": "concept name", "description": "description", "examples": "examples", "references": "references"}],
            "industry_practices": [{"name": "practice name", "description": "description", "companies": "companies using it", "outcomes": "outcomes"}],
            "educational_resources": [{"title": "resource title", "type": "resource type", "url": "url", "description": "description", "topics": "topics"}],
            "market_research": [{"title": "research title", "date": "date", "source": "source", "findings": "findings", "implications": "implications"}]
        }
        """
    elif document_type == "Market Research":
        prompt = """
        Extract market research insights from this document.
        
        Format your response as a JSON object with this key:
        {
            "market_research": [{"title": "research title", "date": "date", "source": "source", "findings": "findings", "implications": "implications for game development"}]
        }
        """
    elif document_type == "Game Concept":
        prompt = """
        Extract game design concepts from this document.
        
        Format your response as a JSON object with this key:
        {
            "design_concepts": [{"name": "concept name", "description": "description", "examples": "examples", "references": "references"}]
        }
        """
    else:
        prompt = """
        Extract game development knowledge from this document, including:
        1. Game design concepts and mechanics
        2. Industry practices mentioned
        3. Educational resources referenced
        4. Market research insights
        
        Format your response as a JSON object with these keys:
        {
            "design_concepts": [{"name": "concept name", "description": "description", "examples": "examples", "references": "references"}],
            "industry_practices": [{"name": "practice name", "description": "description", "companies": "companies using it", "outcomes": "outcomes"}],
            "educational_resources": [{"title": "resource title", "type": "resource type", "url": "url", "description": "description", "topics": "topics"}],
            "market_research": [{"title": "research title", "date": "date", "source": "source", "findings": "findings", "implications": "implications"}]
        }
        """
    
    # Limit text length to avoid token limits
    max_text_length = 15000  # Adjust based on token limits
    if len(text) > max_text_length:
        text = text[:max_text_length] + "..."
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a game design knowledge extraction assistant. Extract structured information from game design documents."},
                {"role": "user", "content": prompt + "\n\nDocument text:\n" + text}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract JSON from the response
            try:
                # Find JSON in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
                else:
                    logger.error("No JSON found in OpenAI response")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from OpenAI response: {str(e)}")
                return None
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None

def save_extracted_knowledge(knowledge_data, knowledge_base):
    """Save extracted knowledge to the knowledge base."""
    if not knowledge_data:
        return 0
    
    count = 0
    
    # Save design concepts
    if "design_concepts" in knowledge_data:
        for concept in knowledge_data["design_concepts"]:
            try:
                knowledge_base.add_design_concept(
                    concept.get("name", ""),
                    concept.get("description", ""),
                    concept.get("examples", ""),
                    concept.get("references", "")
                )
                count += 1
            except Exception as e:
                logger.error(f"Error saving design concept: {str(e)}")
    
    # Save industry practices
    if "industry_practices" in knowledge_data:
        for practice in knowledge_data["industry_practices"]:
            try:
                knowledge_base.add_industry_practice(
                    practice.get("name", ""),
                    practice.get("description", ""),
                    practice.get("companies", ""),
                    practice.get("outcomes", "")
                )
                count += 1
            except Exception as e:
                logger.error(f"Error saving industry practice: {str(e)}")
    
    # Save educational resources
    if "educational_resources" in knowledge_data:
        for resource in knowledge_data["educational_resources"]:
            try:
                knowledge_base.add_educational_resource(
                    resource.get("title", ""),
                    resource.get("type", "Other"),
                    resource.get("url", ""),
                    resource.get("description", ""),
                    resource.get("topics", "")
                )
                count += 1
            except Exception as e:
                logger.error(f"Error saving educational resource: {str(e)}")
    
    # Save market research
    if "market_research" in knowledge_data:
        for research in knowledge_data["market_research"]:
            try:
                knowledge_base.add_market_research(
                    research.get("title", ""),
                    research.get("date", ""),
                    research.get("source", ""),
                    research.get("findings", ""),
                    research.get("implications", "")
                )
                count += 1
            except Exception as e:
                logger.error(f"Error saving market research: {str(e)}")
    
    return count

def display_document_uploader():
    """Display the document uploader interface."""
    st.title("Game Design Document Uploader")
    st.write("Upload game design documents to extract knowledge for Thomas AI.")
    
    # Initialize knowledge base
    try:
        knowledge_base = GameDesignKnowledgeBase()
    except Exception as e:
        st.error(f"Error connecting to knowledge base: {str(e)}")
        logger.error(f"Error initializing knowledge base: {str(e)}")
        return
    
    # Document type selection
    document_type = st.selectbox(
        "Document Type",
        ["Game Design Document", "Market Research", "Game Concept", "Educational Resource", "Other"]
    )
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])
    
    # API Key for OpenAI
    api_key = st.text_input("OpenAI API Key", type="password")
    
    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Extract text based on file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == 'pdf':
            text = extract_text_from_pdf(tmp_path)
        elif file_extension == 'docx':
            text = extract_text_from_docx(tmp_path)
        elif file_extension == 'txt':
            text = extract_text_from_txt(tmp_path)
        else:
            text = ""
            st.error("Unsupported file format")
        
        # Clean up the temporary file
        os.unlink(tmp_path)
        
        # Display text preview
        with st.expander("Document Text Preview"):
            st.text_area("Extracted Text", text[:1000] + "..." if len(text) > 1000 else text, height=200)
        
        # Process button
        if st.button("Extract Knowledge"):
            if not api_key:
                st.error("Please enter your OpenAI API key")
            elif not text:
                st.error("No text could be extracted from the document")
            else:
                with st.spinner("Analyzing document and extracting knowledge..."):
                    # Analyze text with OpenAI
                    knowledge_data = analyze_text_with_openai(text, api_key, document_type)
                    
                    if knowledge_data:
                        # Display extracted knowledge
                        st.success("Knowledge extracted successfully!")
                        
                        # Save to knowledge base
                        items_saved = save_extracted_knowledge(knowledge_data, knowledge_base)
                        st.success(f"Saved {items_saved} knowledge items to the database")
                        
                        # Display the extracted knowledge
                        with st.expander("Extracted Knowledge"):
                            st.json(knowledge_data)
                    else:
                        st.error("Failed to extract knowledge from the document")

if __name__ == "__main__":
    display_document_uploader() 