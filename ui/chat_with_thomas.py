import streamlit as st
import requests
import json
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import OpenAI API helper
from services.ai_assistant import ThomasAIAssistant

def main():
    # Remove the set_page_config call from here since it's called in dashboard.py
    # st.set_page_config(
    #     page_title="Chat with Thomas AI",
    #     page_icon="💬",
    #     layout="wide"
    # )

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "assistant" not in st.session_state:
        st.session_state.assistant = ThomasAIAssistant()

    # API URL for data context
    API_BASE_URL = "http://localhost:8002"

    # Function to get data from API
    def get_data(endpoint):
        try:
            response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Failed to fetch data: {str(e)}")
            return None

    # Display header
    st.title("💬 Chat with Thomas AI")
    st.markdown("Your AI Chief Operating Officer for game development management")
    
    # Add a description of Thomas AI's capabilities
    with st.expander("About Thomas AI - Your Game Development Partner", expanded=False):
        st.markdown("""
        ## Thomas AI Capabilities
        
        Thomas AI is your AI Chief Operating Officer, specialized in game development management and designed to provide industry-leading expertise and support. Thomas is built with extensive knowledge of:
        
        ### Game Design & Development
        - **Game Mechanics Design**: Advising on core gameplay loops, mechanics, and systems
        - **Game Economy Design**: Balancing in-game economies, monetization strategies, and player progression
        - **Development Pipelines**: Optimizing workflows for efficient game production
        - **Platform-Specific Considerations**: Knowledge of requirements for different platforms (mobile, PC, console)
        
        ### Project Management
        - **Production Timelines**: Creating and managing realistic development schedules
        - **Resource Allocation**: Optimizing team resources across different game projects
        - **Risk Assessment**: Identifying potential bottlenecks and development risks
        - **Milestone Planning**: Breaking projects into manageable phases with clear deliverables
        
        ### Financial Management
        - **Budget Planning**: Creating and managing game development budgets
        - **Cost Tracking**: Monitoring expenses across projects and teams
        - **ROI Analysis**: Assessing potential returns on different game features or projects
        - **Funding Options**: Knowledge of different funding models for game development
        
        ### Team Management
        - **Team Structure**: Advising on optimal team compositions for different game types
        - **Skill Assessment**: Identifying necessary skills for specific game projects
        - **Contractor Management**: Guidelines for working with external partners and freelancers
        
        ### Market Intelligence
        - **Industry Trends**: Knowledge of current and emerging trends in game development
        - **Competitive Analysis**: Understanding the market landscape for different game genres
        - **Player Demographics**: Insights into target audiences for various game types
        - **Marketing Strategies**: Approaches for player acquisition and community building
        
        ### Technical Knowledge
        - **Engine Capabilities**: Understanding of game engine features and limitations
        - **Performance Optimization**: Strategies for optimizing game performance
        - **Cross-Platform Development**: Considerations for multi-platform releases
        - **Technical Requirements**: Knowledge of platform-specific technical requirements
        
        Thomas integrates with your project data to provide contextual, data-driven advice tailored to your specific game projects. Ask questions about any aspect of game development, and Thomas will provide thoughtful, industry-informed responses.
        """)

    # Sidebar for context controls
    st.sidebar.title("Data Context")
    st.sidebar.markdown("Select what information Thomas should have access to:")

    include_projects = st.sidebar.checkbox("Project Information", value=True)
    include_payments = st.sidebar.checkbox("Payment Data", value=True)
    include_employees = st.sidebar.checkbox("Employee Information", value=True)
    include_assets = st.sidebar.checkbox("Asset Progress", value=True)

    if st.sidebar.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.assistant.reset_conversation()
        st.experimental_rerun()
    
    # Add a help section with usage examples
    with st.sidebar.expander("How to use Thomas AI", expanded=False):
        st.markdown("""
        ### Getting the Most from Thomas AI
        
        Thomas AI works best when you:
        
        1. **Be Specific**: Ask detailed questions about your game projects
        2. **Provide Context**: Enable relevant data contexts in the sidebar
        3. **Ask Follow-ups**: Dive deeper with follow-up questions
        4. **Explore Topics**: Ask about game design, team management, finances, or market trends
        
        Thomas continuously learns and improves based on your interactions!
        """)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gather context data based on sidebar selections
        context_data = {}
        
        if include_projects:
            projects = get_data("projects/")
            if projects:
                context_data["projects"] = projects
        
        if include_payments:
            payments = get_data("payments/")
            if payments:
                context_data["payments"] = payments
        
        if include_employees:
            employees = get_data("payments/employees")
            if employees:
                context_data["employees"] = employees
                
                # Get more detailed employee payment information
                employee_payments = {}
                for employee in employees[:5]:  # Limit to avoid too many requests
                    emp_payments = get_data(f"payments/employee/{employee}")
                    if emp_payments:
                        employee_payments[employee] = emp_payments
                
                if employee_payments:
                    context_data["employee_payments"] = employee_payments
        
        if include_assets:
            # This would require an assets endpoint to be implemented
            assets = get_data("assets/")
            if assets:
                context_data["assets"] = assets
        
        # Get response from Thomas
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thomas is thinking...")
            
            if context_data:
                response = st.session_state.assistant.ask(prompt, include_data=context_data)
            else:
                response = st.session_state.assistant.ask(prompt)
            
            message_placeholder.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Add some helpful information in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Example Questions")
    st.sidebar.markdown("""
    - "What are the current trends in free-to-play mobile game monetization?"
    - "How should we structure our team for a mid-sized MMORPG project?"
    - "What's a reasonable budget allocation for marketing a indie roguelike game?"
    - "What should our development timeline look like for a casual mobile puzzle game?"
    - "How can we improve player retention in our battle royale game?"
    - "What metrics should we track for our free-to-play mobile game?"
    """)

if __name__ == "__main__":
    main()
