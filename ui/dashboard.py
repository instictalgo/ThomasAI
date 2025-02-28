import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import logging
import threading
import json
import sys
import os

# Import project detail view
from ui.project_detail import display_project_detail
from ui.knowledge_manager import display_knowledge_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("streamlit_dashboard")

# Set the base URL for our API
API_BASE_URL = "http://localhost:8002"

# Create a cache dict for API responses to improve performance
response_cache = {}
cache_ttl = 60  # TTL in seconds

# Function to get data from API with caching
def api_get(endpoint, default=None, use_cache=True, retries=3, timeout=3):
    cache_key = endpoint
    
    # Return cached response if available and not expired
    current_time = time.time()
    if use_cache and cache_key in response_cache:
        cached_time, cached_data = response_cache[cache_key]
        if current_time - cached_time < cache_ttl:
            return cached_data
    
    # Make API request with retries
    for i in range(retries):
        try:
            start_time = time.time()
            response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=timeout)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                # Cache the successful response
                if use_cache:
                    response_cache[cache_key] = (current_time, data)
                
                # Log successful response
                logger.info(f"API call to {endpoint} successful ({elapsed:.2f}s)")
                return data
            else:
                logger.warning(f"API call to {endpoint} failed with status {response.status_code}")
                # Only retry on 5xx errors
                if response.status_code < 500:
                    break
                time.sleep(0.5)
        except requests.exceptions.Timeout:
            logger.warning(f"API call to {endpoint} timed out (attempt {i+1})")
        except Exception as e:
            logger.warning(f"API call to {endpoint} failed: {str(e)}")
            time.sleep(0.5)
    
    # Return default if all retries failed
    return default

# Configure the page with a modern design
st.set_page_config(
    page_title="Thomas AI Management System",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for a modern look
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #2563EB;
        border: none;
    }
    .css-1aumxhk {
        background-color: #F1F5F9;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .st-bq {
        border-left-color: #2563EB !important;
    }
    .streamlit-expanderHeader {
        background-color: #F1F5F9;
        border-radius: 4px;
    }
    .stMetric {
        background-color: #F1F5F9;
        border-radius: 10px;
        padding: 1rem;
    }
    div.stMetric > div {
        text-align: center;
    }
    div.stMetric label {
        color: #1E3A8A !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# Sidebar navigation
st.sidebar.title("Navigation")
page_selections = ["Dashboard", "Projects", "Finance", "Team", "Assets", "Knowledge", "System"]
selected_page = st.sidebar.radio("Go to", page_selections)

# Update the page state when a new page is selected
if selected_page != st.session_state.page:
    # Reset any page-specific state if needed
    if selected_page == 'Dashboard':
        # Reset any dashboard-specific state
        pass
    
    st.session_state.page = selected_page
    st.experimental_rerun()

# Main content
st.title("🎮 Thomas AI Management System")

# Display different content based on the current page
if st.session_state.page == 'Dashboard':
    display_dashboard()
elif st.session_state.page == 'Projects':
    display_projects_page()
elif st.session_state.page == 'Finance':
    display_finance_page()
elif st.session_state.page == 'Team':
    display_team_page()
elif st.session_state.page == 'Assets':
    display_assets_page()
elif st.session_state.page == 'Knowledge':
    display_knowledge_manager()
elif st.session_state.page == 'System':
    display_system_page()
elif st.session_state.page == 'Project Detail' and 'current_project' in st.session_state:
    # Go back button
    if st.button("← Back to Projects"):
        st.session_state.page = 'Projects'
        st.experimental_rerun()
    
    # Display the project detail
    display_project_detail(st.session_state.current_project)
else:
    # Default to dashboard if the page is not recognized
    st.session_state.page = 'Dashboard'
    st.experimental_rerun()

# Define page content functions
def display_dashboard():
    """Display the main dashboard content"""
    st.subheader("📊 Overview")

    # Summary metrics at the top
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch summary data
    projects_count = len(api_get("projects/", []))
    
    # Project metrics
    with col1:
        st.metric("Active Projects", projects_count)
        
    # Payment metrics
    payments = api_get("payments/", [])
    if payments:
        total_usd = sum(p.get("amount", 0) for p in payments if p.get("currency") == "USD")
        with col2:
            st.metric("Total Payments", f"${total_usd:,.2f}")
    else:
        with col2:
            st.metric("Total Payments", "$0.00")
    
    # Team metrics
    employees = api_get("payments/employees", [])
    with col3:
        st.metric("Team Members", len(employees) if employees else 0)
    
    # Asset metrics
    assets = api_get("assets/", [])
    with col4:
        st.metric("Assets", len(assets) if assets else 0)
    
    # Active Projects
    st.subheader("Active Projects")
    
    # Get projects data
    projects = api_get("projects/", [])
    
    if projects:
        # Create a nice grid of project cards
        cols = st.columns(3)
        for i, project in enumerate(projects):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"### {project.get('name', 'Unnamed Project')}")
                    st.progress(0.6)  # Mock progress - would need real data
                    st.markdown(f"**Budget:** ${project.get('total_budget', 0):,.2f}")
                    st.markdown(f"**Timeline:** {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}")
                    if st.button(f"View Details", key=f"view_{project.get('id')}"):
                        st.session_state.current_project = project.get('id')
                        st.session_state.page = 'Project Detail'
                        st.experimental_rerun()
    else:
        st.info("No projects found. Create a project to get started.")
    
    # Recent payments
    st.subheader("Recent Payments")
    
    if payments:
        # Create a dataframe for the payments
        payment_data = []
        for payment in payments[:5]:  # Show only the 5 most recent payments
            payment_data.append({
                "Date": payment.get("date", "N/A"),
                "Recipient": payment.get("recipient", "Unknown"),
                "Amount": f"{payment.get('currency', 'USD')} {payment.get('amount', 0):,.2f}",
                "Project": payment.get("project", "N/A"),
                "Status": payment.get("status", "Completed")
            })
        
        payment_df = pd.DataFrame(payment_data)
        st.table(payment_df)
    else:
        st.info("No payment data available.")
    
    # Financial overview chart
    st.subheader("Financial Overview")
    
    if payments:
        # Group payments by month and project
        payment_by_month_project = {}
        for payment in payments:
            date = payment.get("date", "")
            if date:
                month = date[:7]  # Get YYYY-MM
                project = payment.get("project", "Unknown")
                amount = payment.get("amount", 0)
                currency = payment.get("currency", "USD")
                
                # Convert to USD for consistency
                usd_amount = amount
                if currency == "SOL":
                    usd_amount = amount * 150  # Assuming 1 SOL = $150 USD
                
                if month not in payment_by_month_project:
                    payment_by_month_project[month] = {}
                
                if project not in payment_by_month_project[month]:
                    payment_by_month_project[month][project] = 0
                
                payment_by_month_project[month][project] += usd_amount
        
        # Convert to dataframe
        fin_data = []
        for month, projects in payment_by_month_project.items():
            for project, amount in projects.items():
                fin_data.append({
                    "Month": month,
                    "Project": project,
                    "Amount": amount
                })
        
        if fin_data:
            fin_df = pd.DataFrame(fin_data)
            
            # Sort by month
            fin_df["Month"] = pd.to_datetime(fin_df["Month"])
            fin_df = fin_df.sort_values("Month")
            fin_df["Month"] = fin_df["Month"].dt.strftime("%b %Y")
            
            # Create a stacked bar chart
            fig = px.bar(
                fin_df, 
                x="Month", 
                y="Amount", 
                color="Project",
                title="Monthly Payments by Project (USD)",
                labels={"Amount": "Amount (USD)", "Month": ""},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            st.plotly_chart(fig)
        else:
            st.info("Not enough financial data for visualization.")
    else:
        st.info("No financial data available.")

def display_projects_page():
    """Display the projects page content"""
    st.subheader("📁 Projects")
    
    # Add new project form
    with st.expander("Add New Project"):
        with st.form("new_project_form"):
            project_name = st.text_input("Project Name")
            project_description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
            
            budget = st.number_input("Budget (USD)", min_value=0.0, step=1000.0)
            
            submit_button = st.form_submit_button("Create Project")
            
            if submit_button:
                if project_name:
                    # Format the data for the API
                    new_project = {
                        "name": project_name,
                        "description": project_description,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "total_budget": budget
                    }
                    
                    # Send to the API
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/projects/",
                            json=new_project
                        )
                        
                        if response.status_code == 200 or response.status_code == 201:
                            st.success("Project created successfully!")
                            # Clear cache to show the new project
                            if "projects/" in response_cache:
                                del response_cache["projects/"]
                            # Refresh the page
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error(f"Failed to create project: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Project name is required")
    
    # List all projects
    projects = api_get("projects/", [])
    
    if projects:
        # Create a nice grid of project cards
        cols = st.columns(3)
        for i, project in enumerate(projects):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"### {project.get('name', 'Unnamed Project')}")
                    st.progress(0.6)  # Mock progress - would need real data
                    st.markdown(f"**Budget:** ${project.get('total_budget', 0):,.2f}")
                    st.markdown(f"**Timeline:** {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}")
                    if st.button(f"View Details", key=f"view_{project.get('id')}"):
                        st.session_state.current_project = project.get('id')
                        st.session_state.page = 'Project Detail'
                        st.experimental_rerun()
    else:
        st.info("No projects found. Create a project to get started.")

def display_finance_page():
    """Display the finance page content"""
    st.subheader("💰 Finance")
    
    # Add new payment form
    with st.expander("Add New Payment"):
        with st.form("new_payment_form"):
            projects = api_get("projects/", [])
            project_names = ["None"] + [p["name"] for p in projects]
            selected_project = st.selectbox("Project", project_names)
            
            recipient = st.text_input("Recipient")
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            
            currency = st.selectbox("Currency", ["USD", "SOL"])
            payment_date = st.date_input("Payment Date")
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "PayPal", "Crypto", "Check", "Cash"])
            
            submit_button = st.form_submit_button("Record Payment")
            
            if submit_button:
                if recipient and amount > 0:
                    # Get project ID if a project was selected
                    project_id = None
                    if selected_project != "None":
                        for p in projects:
                            if p["name"] == selected_project:
                                project_id = p["id"]
                                break
                    
                    # Format the data for the API
                    new_payment = {
                        "recipient": recipient,
                        "amount": amount,
                        "currency": currency,
                        "date": payment_date.isoformat(),
                        "method": payment_method,
                        "project": project_id
                    }
                    
                    # Send to the API
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/payments/",
                            json=new_payment
                        )
                        
                        if response.status_code == 200 or response.status_code == 201:
                            st.success("Payment recorded successfully!")
                            # Clear cache to show the new payment
                            if "payments/" in response_cache:
                                del response_cache["payments/"]
                            # Refresh the page
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error(f"Failed to record payment: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Recipient and amount are required")
    
    # List all payments
    payments = api_get("payments/", [])
    
    if payments:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["All Payments", "By Project", "By Recipient"])
        
        with tab1:
            # Create a dataframe for the payments
            payment_data = []
            for payment in payments:
                payment_data.append({
                    "Date": payment.get("date", "N/A"),
                    "Recipient": payment.get("recipient", "Unknown"),
                    "Amount": payment.get("amount", 0),
                    "Currency": payment.get("currency", "USD"),
                    "Project": payment.get("project", "N/A"),
                    "Method": payment.get("method", "N/A")
                })
            
            if payment_data:
                payment_df = pd.DataFrame(payment_data)
                
                # Sort by date
                payment_df["Date"] = pd.to_datetime(payment_df["Date"])
                payment_df = payment_df.sort_values("Date", ascending=False)
                payment_df["Date"] = payment_df["Date"].dt.strftime("%Y-%m-%d")
                
                # Display as a table
                st.dataframe(payment_df)
            else:
                st.info("No payment data available.")
        
        with tab2:
            # Group payments by project
            payment_by_project = {}
            for payment in payments:
                project = payment.get("project", "Unknown")
                amount = payment.get("amount", 0)
                currency = payment.get("currency", "USD")
                
                if project not in payment_by_project:
                    payment_by_project[project] = {"USD": 0, "SOL": 0}
                
                payment_by_project[project][currency] += amount
            
            # Create a dataframe
            project_data = []
            for project, amounts in payment_by_project.items():
                project_data.append({
                    "Project": project,
                    "USD": amounts["USD"],
                    "SOL": amounts["SOL"],
                    "Total (USD)": amounts["USD"] + (amounts["SOL"] * 150)  # Assuming 1 SOL = $150 USD
                })
            
            if project_data:
                project_df = pd.DataFrame(project_data)
                project_df = project_df.sort_values("Total (USD)", ascending=False)
                
                # Display as a table
                st.dataframe(project_df)
                
                # Create a pie chart of payment distribution
                fig = px.pie(
                    project_df, 
                    values="Total (USD)",
                    names="Project",
                    title="Payment Distribution by Project",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                st.plotly_chart(fig)
            else:
                st.info("No payment data available.")
        
        with tab3:
            # Group payments by recipient
            payment_by_recipient = {}
            for payment in payments:
                recipient = payment.get("recipient", "Unknown")
                amount = payment.get("amount", 0)
                currency = payment.get("currency", "USD")
                
                if recipient not in payment_by_recipient:
                    payment_by_recipient[recipient] = {"USD": 0, "SOL": 0}
                
                payment_by_recipient[recipient][currency] += amount
            
            # Create a dataframe
            recipient_data = []
            for recipient, amounts in payment_by_recipient.items():
                recipient_data.append({
                    "Recipient": recipient,
                    "USD": amounts["USD"],
                    "SOL": amounts["SOL"],
                    "Total (USD)": amounts["USD"] + (amounts["SOL"] * 150)  # Assuming 1 SOL = $150 USD
                })
            
            if recipient_data:
                recipient_df = pd.DataFrame(recipient_data)
                recipient_df = recipient_df.sort_values("Total (USD)", ascending=False)
                
                # Display as a table
                st.dataframe(recipient_df)
                
                # Create a bar chart of payment distribution
                fig = px.bar(
                    recipient_df, 
                    x="Recipient",
                    y="Total (USD)",
                    title="Total Payments by Recipient",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                st.plotly_chart(fig)
            else:
                st.info("No payment data available.")
    else:
        st.info("No payment data available. Record a payment to get started.")

def display_team_page():
    """Display the team page content"""
    st.subheader("👥 Team")
    
    # List all team members (derived from payment recipients)
    employees = api_get("payments/employees", [])
    
    if employees:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Team Members", "Payment History"])
        
        with tab1:
            # Create a grid of team member cards
            cols = st.columns(4)
            for i, employee in enumerate(employees):
                with cols[i % 4]:
                    with st.container():
                        st.markdown(f"### {employee}")
                        st.markdown("**Role:** Developer")  # This would come from a real data source
                        
                        # Get payments for this employee
                        employee_payments = api_get(f"payments/employee/{employee}", [])
                        
                        if employee_payments:
                            total_usd = sum(p.get("amount", 0) for p in employee_payments if p.get("currency") == "USD")
                            total_sol = sum(p.get("amount", 0) for p in employee_payments if p.get("currency") == "SOL")
                            
                            st.markdown(f"**Total Paid:** ${total_usd:,.2f} USD, {total_sol:,.2f} SOL")
                            st.markdown(f"**Last Payment:** {employee_payments[0].get('date', 'N/A')}")
        
        with tab2:
            # Display payment history for all team members
            payment_data = []
            for employee in employees:
                employee_payments = api_get(f"payments/employee/{employee}", [])
                
                for payment in employee_payments:
                    payment_data.append({
                        "Date": payment.get("date", "N/A"),
                        "Recipient": employee,
                        "Amount": payment.get("amount", 0),
                        "Currency": payment.get("currency", "USD"),
                        "Project": payment.get("project", "N/A"),
                        "Method": payment.get("method", "N/A")
                    })
            
            if payment_data:
                payment_df = pd.DataFrame(payment_data)
                
                # Sort by date
                payment_df["Date"] = pd.to_datetime(payment_df["Date"])
                payment_df = payment_df.sort_values("Date", ascending=False)
                payment_df["Date"] = payment_df["Date"].dt.strftime("%Y-%m-%d")
                
                # Display as a table
                st.dataframe(payment_df)
            else:
                st.info("No payment data available.")
    else:
        st.info("No team members found. Record a payment to add team members.")

def display_assets_page():
    """Display the assets page content"""
    st.subheader("🎨 Assets")
    
    # Add new asset form
    with st.expander("Add New Asset"):
        with st.form("new_asset_form"):
            projects = api_get("projects/", [])
            project_names = [p["name"] for p in projects] if projects else ["None"]
            selected_project = st.selectbox("Project", project_names)
            
            asset_name = st.text_input("Asset Name")
            asset_type = st.selectbox("Asset Type", ["3D Model", "Texture", "Animation", "Sound", "Script", "UI", "Other"])
            status = st.selectbox("Status", ["Not Started", "In Progress", "Review", "Completed"])
            progress = st.slider("Progress", 0, 100, 0)
            
            employees = api_get("payments/employees", [])
            assigned_to = st.selectbox("Assigned To", ["Unassigned"] + employees if employees else ["Unassigned"])
            
            due_date = st.date_input("Due Date")
            
            submit_button = st.form_submit_button("Add Asset")
            
            if submit_button:
                if asset_name and selected_project != "None":
                    # Get project ID
                    project_id = None
                    for p in projects:
                        if p["name"] == selected_project:
                            project_id = p["id"]
                            break
                    
                    # Format the data for the API
                    new_asset = {
                        "name": asset_name,
                        "asset_type": asset_type,
                        "status": status,
                        "progress": progress,
                        "assigned_to": assigned_to if assigned_to != "Unassigned" else None,
                        "due_date": due_date.isoformat(),
                        "project_id": project_id
                    }
                    
                    # Send to the API
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/assets/",
                            json=new_asset
                        )
                        
                        if response.status_code == 200 or response.status_code == 201:
                            st.success("Asset added successfully!")
                            # Clear cache to show the new asset
                            if "assets/" in response_cache:
                                del response_cache["assets/"]
                            # Refresh the page
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error(f"Failed to add asset: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Asset name and project are required")
    
    # List all assets
    assets = api_get("assets/", [])
    
    if assets:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["All Assets", "By Project", "By Status"])
        
        with tab1:
            # Create a dataframe for the assets
            asset_data = []
            for asset in assets:
                asset_data.append({
                    "Name": asset.get("name", "Unnamed"),
                    "Type": asset.get("asset_type", "Unknown"),
                    "Status": asset.get("status", "Unknown"),
                    "Progress": asset.get("progress", 0),
                    "Assigned To": asset.get("assigned_to", "Unassigned"),
                    "Due Date": asset.get("due_date", "N/A"),
                    "Project": asset.get("project", "Unknown")
                })
            
            if asset_data:
                asset_df = pd.DataFrame(asset_data)
                
                # Sort by due date
                asset_df["Due Date"] = pd.to_datetime(asset_df["Due Date"])
                asset_df = asset_df.sort_values("Due Date")
                asset_df["Due Date"] = asset_df["Due Date"].dt.strftime("%Y-%m-%d")
                
                # Display as a table
                st.dataframe(asset_df)
            else:
                st.info("No asset data available.")
        
        with tab2:
            # Group assets by project
            asset_by_project = {}
            for asset in assets:
                project = asset.get("project", "Unknown")
                
                if project not in asset_by_project:
                    asset_by_project[project] = []
                
                asset_by_project[project].append(asset)
            
            # Create tabs for each project
            project_tabs = st.tabs(list(asset_by_project.keys()))
            
            for i, (project, project_assets) in enumerate(asset_by_project.items()):
                with project_tabs[i]:
                    for asset in project_assets:
                        with st.expander(f"{asset.get('name', 'Unnamed Asset')} - {asset.get('progress', 0)}% complete"):
                            st.write(f"**Type:** {asset.get('asset_type', 'Unknown')}")
                            st.write(f"**Assigned to:** {asset.get('assigned_to', 'Unassigned')}")
                            st.write(f"**Status:** {asset.get('status', 'Unknown')}")
                            st.write(f"**Due date:** {asset.get('due_date', 'Not set')}")
                            st.progress(asset.get('progress', 0) / 100)
        
        with tab3:
            # Group assets by status
            asset_by_status = {}
            for asset in assets:
                status = asset.get("status", "Unknown")
                
                if status not in asset_by_status:
                    asset_by_status[status] = []
                
                asset_by_status[status].append(asset)
            
            # Create a visualization of assets by status
            status_counts = {status: len(assets) for status, assets in asset_by_status.items()}
            
            # Create a bar chart
            status_df = pd.DataFrame({
                "Status": list(status_counts.keys()),
                "Count": list(status_counts.values())
            })
            
            fig = px.bar(
                status_df, 
                x="Status",
                y="Count",
                title="Assets by Status",
                color="Status",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            st.plotly_chart(fig)
            
            # Create tabs for each status
            status_tabs = st.tabs(list(asset_by_status.keys()))
            
            for i, (status, status_assets) in enumerate(asset_by_status.items()):
                with status_tabs[i]:
                    for asset in status_assets:
                        with st.expander(f"{asset.get('name', 'Unnamed Asset')} - {asset.get('project', 'Unknown')}"):
                            st.write(f"**Type:** {asset.get('asset_type', 'Unknown')}")
                            st.write(f"**Assigned to:** {asset.get('assigned_to', 'Unassigned')}")
                            st.write(f"**Progress:** {asset.get('progress', 0)}%")
                            st.write(f"**Due date:** {asset.get('due_date', 'Not set')}")
                            st.progress(asset.get('progress', 0) / 100)
    else:
        st.info("No assets found. Add an asset to get started.")

def display_system_page():
    """Display the system settings and status page"""
    st.subheader("⚙️ System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Status")
        
        # Check API health
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=3)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                st.success("✅ API Service is running normally")
                
                # Display API health information
                st.json(health_data)
            else:
                st.error(f"❌ API Service is not responding properly (Status: {health_response.status_code})")
        except Exception as e:
            st.error(f"❌ Could not connect to API Server: {str(e)}")
    
    with col2:
        st.subheader("System Information")
        
        # Try to get system stats
        try:
            import psutil
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.5)
            st.metric("CPU Usage", f"{cpu_percent}%")
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024 * 1024 * 1024)  # Convert to GB
            memory_total = memory.total / (1024 * 1024 * 1024)  # Convert to GB
            st.metric("Memory Usage", f"{memory_percent}% ({memory_used:.2f} GB / {memory_total:.2f} GB)")
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024 * 1024 * 1024)  # Convert to GB
            disk_total = disk.total / (1024 * 1024 * 1024)  # Convert to GB
            st.metric("Disk Usage", f"{disk_percent}% ({disk_used:.2f} GB / {disk_total:.2f} GB)")
        except:
            st.warning("Could not retrieve system statistics. The psutil module may not be installed.")
    
    # Performance Tests
    st.subheader("Performance Tests")
    
    if st.button("Run Performance Test"):
        with st.spinner("Running performance tests..."):
            endpoints = [
                "health",
                "projects/",
                "payments/"
            ]
            
            results = []
            for endpoint in endpoints:
                start_time = time.time()
                try:
                    response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
                    response_time = time.time() - start_time
                    status = response.status_code
                    
                    # Get response size
                    size = len(response.content)
                    size_kb = size / 1024
                    
                    results.append({
                        "endpoint": endpoint,
                        "status": status,
                        "time": response_time,
                        "size": size_kb
                    })
                except Exception as e:
                    results.append({
                        "endpoint": endpoint,
                        "status": "Error",
                        "time": time.time() - start_time,
                        "size": 0,
                        "error": str(e)
                    })
            
            # Display results in a DataFrame
            df = pd.DataFrame(results)
            st.write(df)
            
            # Plot response times
            if not df.empty:
                fig = px.bar(df, x="endpoint", y="time", 
                           title="API Response Times (seconds)",
                           labels={"endpoint": "Endpoint", "time": "Response Time (s)"})
                st.plotly_chart(fig)
    
    # Database Information
    st.subheader("Database Tables")
    
    # Request database schema information if available
    try:
        tables = api_get("schema/tables", [])
        if tables:
            for table in tables:
                with st.expander(f"Table: {table['name']}"):
                    st.write(f"Row count: {table.get('row_count', 'Unknown')}")
                    if 'columns' in table:
                        st.dataframe(pd.DataFrame(table['columns']))
        else:
            st.info("Database schema information not available")
    except:
        st.warning("Could not retrieve database schema information")

# Modern footer with useful links and information
st.sidebar.markdown("---")
st.sidebar.subheader("System Information")
st.sidebar.info(f"""
**Thomas AI Management System v1.0**
- API Status: {'Online ✅' if api_get('', None) is not None else 'Offline ❌'}
- Database: {'Connected ✅' if api_get('projects/', None) is not None else 'Disconnected ❌'}
""")

# Help information
with st.sidebar.expander("Help & Resources"):
    st.markdown("""
    - [System Documentation](https://github.com/yourusername/thomas-ai/)
    - [Report an Issue](https://github.com/yourusername/thomas-ai/issues)
    - [API Reference](http://localhost:8002/docs)
    """)
