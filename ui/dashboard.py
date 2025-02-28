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

# Title and description
st.title("🎮 Thomas AI Management System")
st.markdown("""
Your all-in-one dashboard for managing game development projects, payments, and assets.
""")

# Sidebar navigation with modern styling
st.sidebar.image("https://i.imgur.com/ZDxo6FA.png", width=50)  # Replace with your logo
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Payments", "Payment Details", "Projects", "Chat with Thomas", "Assets", "System Status"]
)

# Dashboard main page
if page == "Dashboard":
    # Get data for dashboard
    projects = api_get("projects/", [])
    payments = api_get("payments/", [])
    
    # Show key metrics
    st.subheader("Business Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Projects", len(projects) if projects else 0)
    
    with col2:
        if payments:
            # Convert SOL to USD for correct total calculation
            total_usd = sum(p.get("amount", 0) for p in payments if p.get("currency") == "USD")
            total_sol = sum(p.get("amount", 0) for p in payments if p.get("currency") == "SOL")
            # Assuming 1 SOL = 150 USD for conversion
            total_payments = total_usd + (total_sol * 150)
            st.metric("Total Payments", f"${total_payments:,.2f}")
        else:
            st.metric("Total Payments", "$0")
    
    with col3:
        if payments:
            employees = len(set(p.get("employee_id", "") for p in payments))
            st.metric("Team Members", employees)
        else:
            st.metric("Team Members", 0)
    
    # Projects overview
    st.subheader("Projects")
    
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
        # Sort by date (newest first)
        payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Show only the 5 most recent payments
        recent_payments = payments[:5]
        payment_data = []
        
        for p in recent_payments:
            payment_data.append({
                "Date": p.get("created_at", "Unknown"),
                "Employee": p.get("employee_id", "Unknown"),
                "Amount": f"{p.get('currency', '')} {p.get('amount', 0)}",
                "Method": p.get("payment_method", "Unknown"),
                "Status": p.get("status", "Unknown").capitalize()
            })
        
        if payment_data:
            st.table(pd.DataFrame(payment_data))
        else:
            st.info("No payment records found")
    else:
        st.info("No payment records found")

elif page == "Payments":
    st.header("Payment Management")
    
    # Create payment form
    with st.form("payment_form"):
        st.subheader("Create New Payment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            employee_id = st.text_input("Employee Name")
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        
        with col2:
            currency = st.selectbox("Currency", ["USD", "SOL"])
            payment_method = st.selectbox("Payment Method", ["paypal", "crypto_sol", "bank_transfer"])
        
        submitted = st.form_submit_button("Create Payment")
        if submitted:
            if not employee_id:
                st.error("Employee name is required")
            else:
                payment_data = {
                    "employee_id": employee_id,
                    "amount": amount,
                    "currency": currency,
                    "payment_method": payment_method
                }
                try:
                    response = requests.post(f"{API_BASE_URL}/payments/", json=payment_data)
                    if response.status_code == 200:
                        st.success(f"Payment created successfully!")
                    else:
                        st.error(f"Failed to create payment: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
    
    # List payments
    st.subheader("Payment History")
    payments = api_get("payments/", [])
    
    if payments:
        # Sort by date (newest first)
        payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Group by employee
        employees = {}
        for p in payments:
            employee = p.get("employee_id", "Unknown")
            if employee not in employees:
                employees[employee] = []
            employees[employee].append(p)
        
        # Create tabs for All and By Employee
        tab1, tab2 = st.tabs(["All Payments", "By Employee"])
        
        with tab1:
            # Show all payments in a table
            payment_data = []
            for p in payments:
                payment_data.append({
                    "Date": p.get("created_at", "Unknown"),
                    "Employee": p.get("employee_id", "Unknown"),
                    "Amount": f"{p.get('currency', '')} {p.get('amount', 0)}",
                    "USD Equivalent": f"${p.get('amount', 0) * 150:,.2f}" if p.get('currency') == "SOL" else f"${p.get('amount', 0):,.2f}",
                    "Method": p.get("payment_method", "Unknown"),
                    "Status": p.get("status", "Unknown").capitalize()
                })
            
            if payment_data:
                st.dataframe(pd.DataFrame(payment_data))
            else:
                st.info("No payment records found")
        
        with tab2:
            # Show payments grouped by employee
            for employee, emp_payments in employees.items():
                with st.expander(f"{employee} ({len(emp_payments)} payments)"):
                    # Calculate totals
                    total_usd = sum(p.get("amount", 0) for p in emp_payments if p.get("currency") == "USD")
                    total_sol = sum(p.get("amount", 0) for p in emp_payments if p.get("currency") == "SOL")
                    total_equivalent = total_usd + (total_sol * 150)
                    
                    # Show totals
                    st.metric("Total Payments (USD Equivalent)", f"${total_equivalent:,.2f}")
                    
                    # Show payment history
                    emp_payment_data = []
                    for p in emp_payments:
                        emp_payment_data.append({
                            "Date": p.get("created_at", "Unknown"),
                            "Amount": f"{p.get('currency', '')} {p.get('amount', 0)}",
                            "Method": p.get("payment_method", "Unknown"),
                            "Status": p.get("status", "Unknown").capitalize()
                        })
                    
                    st.dataframe(pd.DataFrame(emp_payment_data))
    else:
        st.info("No payment records found")

elif page == "Payment Details":
    st.header("Payment Details by Employee")
    
    # Get all employees
    employees = api_get("payments/employees", [])
    
    if employees:
        selected_employee = st.selectbox("Select Employee", employees)
        
        if selected_employee:
            st.subheader(f"Payment History for {selected_employee}")
            
            # Get payments for selected employee
            employee_payments = api_get(f"payments/employee/{selected_employee}", [])
            
            if employee_payments:
                # Calculate totals
                total_usd = sum(p.get("amount", 0) for p in employee_payments if p.get("currency") == "USD")
                total_sol = sum(p.get("amount", 0) for p in employee_payments if p.get("currency") == "SOL")
                total_equivalent = total_usd + (total_sol * 150)
                
                # Show totals
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total USD", f"${total_usd:,.2f}")
                with col2:
                    st.metric("Total SOL", f"{total_sol:,.2f}")
                with col3:
                    st.metric("USD Equivalent", f"${total_equivalent:,.2f}")
                
                # Prepare data for visualization
                if len(employee_payments) > 1:
                    payment_dates = []
                    payment_amounts = []
                    
                    for payment in sorted(employee_payments, key=lambda x: x.get("created_at", "")):
                        date = payment.get("created_at", "Unknown")
                        amount = payment.get("amount", 0)
                        if payment.get("currency") == "SOL":
                            amount = amount * 150  # Convert to USD
                        
                        payment_dates.append(date)
                        payment_amounts.append(amount)
                    
                    # Create a dataframe for visualization
                    df = pd.DataFrame({
                        "Date": payment_dates,
                        "Amount (USD)": payment_amounts
                    })
                    
                    # Create payment trend visualization
                    fig = px.line(
                        df,
                        x="Date",
                        y="Amount (USD)",
                        title=f"Payments to {selected_employee} Over Time",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show each payment in an expander
                st.subheader("Payment Details")
                
                for payment in sorted(employee_payments, key=lambda x: x.get("created_at", ""), reverse=True):
                    with st.expander(f"Payment on {payment.get('created_at', 'Unknown Date')} - {payment.get('currency', '')} {payment.get('amount', '')}"):
                        cols = st.columns([1, 3])
                        
                        with cols[0]:
                            method = payment.get("payment_method", "").lower()
                            if "paypal" in method:
                                st.image("https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg", width=100)
                            elif "crypto" in method or "sol" in method:
                                st.image("https://cryptologos.cc/logos/solana-sol-logo.png", width=100)
                            elif "bank" in method:
                                st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=100)
                            else:
                                st.image("https://cdn-icons-png.flaticon.com/512/1019/1019607.png", width=100)
                        
                        with cols[1]:
                            st.write(f"**Amount:** {payment.get('currency')} {payment.get('amount')}")
                            if payment.get('currency') == "SOL":
                                st.write(f"**USD Equivalent:** ${payment.get('amount', 0) * 150:,.2f}")
                            st.write(f"**Method:** {payment.get('payment_method', 'Unknown')}")
                            st.write(f"**Status:** {payment.get('status', 'Unknown')}")
                            st.write(f"**Transaction ID:** {payment.get('transaction_id', 'N/A')}")
                            
                            # Add payment link if available
                            if payment.get("payment_link"):
                                st.write(f"**Payment Link:** [View Transaction]({payment.get('payment_link')})")
            else:
                st.info(f"No payments found for {selected_employee}")
    else:
        st.error("Could not retrieve employee list. Is the API server running?")

# Projects page
elif page == "Projects":
    st.header("Project Management")
    
    # Project list with modern styling
    st.subheader("Existing Projects")
    
    projects = api_get("projects/", [])
    if projects:
        # Display projects in cards
        cols = st.columns(3)
        for i, project in enumerate(projects):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"### {project.get('name', 'Unnamed Project')}")
                    st.markdown(f"**Budget:** ${project.get('total_budget', 0):,.2f}")
                    st.markdown(f"**Timeline:** {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}")
                    
                    # Project progress (mock data - would need real calculation)
                    progress = 0.6
                    st.progress(progress)
                    st.markdown(f"**Progress:** {int(progress * 100)}% complete")
                    
                    # Button to view project details
                    if st.button(f"View Details", key=f"view_{project.get('id')}"):
                        # In a real app, this would navigate to a project details page
                        st.session_state.current_project = project.get('id')
                        st.session_state.page = 'Project Detail'
                        st.experimental_rerun()
    else:
        st.info("No projects found. Create a project to get started.")
    
    # Create project form below existing projects
    st.header("Create New Project")
    
    with st.form("project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Project Name")
            total_budget = st.number_input("Total Budget", min_value=1000.0, value=20000.0, format="%.2f")
        
        with col2:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        # Additional fields
        st.subheader("Initial Team")
        team_members = st.text_area("Enter team members (one per line)")
        
        st.subheader("Project Description")
        description = st.text_area("Project description and goals")
        
        submitted = st.form_submit_button("Create Project")
        if submitted:
            if not project_name:
                st.error("Project name is required")
            else:
                project_data = {
                    "name": project_name,
                    "total_budget": total_budget,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "description": description,
                    "team_members": team_members.split("\n") if team_members else []
                }
                try:
                    response = requests.post(f"{API_BASE_URL}/projects/", json=project_data)
                    if response.status_code == 200:
                        st.success(f"Project '{project_name}' created successfully!")
                    else:
                        st.error(f"Failed to create project: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

# Chat with Thomas page
elif page == "Chat with Thomas":
    # Import and run chat interface
    try:
        from ui.chat_with_thomas import main
        main()
    except Exception as e:
        st.error(f"Error loading chat interface: {str(e)}")
        st.info("The Thomas AI chat interface couldn't be loaded. Is the required module installed?")

# Assets page
elif page == "Assets":
    st.header("Asset Management")
    st.info("Asset management interface is under development")

# System Status page
elif page == "System Status":
    st.subheader("System Status")
    
    # Create columns for statuses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Server")
        
        # Check API health
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=3)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                api_data = response.json()
                st.success(f"✅ API Server is running (response time: {response_time:.2f}s)")
                
                # Display API version and timestamp
                st.info(f"API Version: {api_data.get('version', 'Unknown')}")
                timestamp = api_data.get('timestamp')
                if timestamp:
                    try:
                        timestamp_dt = datetime.fromisoformat(timestamp)
                        st.info(f"Server Time: {timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        st.info(f"Server Time: {timestamp}")
                
                # Display database status
                if api_data.get('database') == 'connected':
                    st.success("✅ Database is connected")
                else:
                    st.error(f"❌ Database is disconnected: {api_data.get('error', 'Unknown error')}")
            else:
                st.error(f"❌ API server returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to API Server: Connection refused")
        except requests.exceptions.Timeout:
            st.error("❌ API Server connection timed out")
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
