import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def display_project_detail(project_id):
    API_BASE_URL = "http://localhost:8002"
    
    # Fetch project details
    try:
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}")
        if response.status_code == 200:
            project = response.json()
        else:
            st.error(f"Failed to fetch project details: {response.status_code}")
            return
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return
    
    # Display project header
    st.title(f"{project.get('name', 'Project Detail')}")
    
    # Project metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"${project.get('total_budget', 0):,.2f}")
    with col2:
        st.metric("Start Date", project.get('start_date', 'Unknown'))
    with col3:
        st.metric("End Date", project.get('end_date', 'Unknown'))
    
    # Fetch expenses for this project
    try:
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/expenses")
        if response.status_code == 200:
            expenses = response.json()
        else:
            expenses = []
    except:
        expenses = []
    
    # Calculate budget metrics
    total_spent = sum(expense.get('amount', 0) for expense in expenses)
    remaining_budget = project.get('total_budget', 0) - total_spent
    
    # Budget overview
    st.header("Budget Overview")
    
    # Budget progress bar
    if project.get('total_budget', 0) > 0:
        progress = total_spent / project.get('total_budget', 0)
        st.progress(min(progress, 1.0))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Spent", f"${total_spent:,.2f}")
        with col2:
            st.metric("Remaining Budget", f"${remaining_budget:,.2f}")
    
    # Create budget visualization
    if expenses:
        # Prepare data for pie chart by category
        expense_by_category = {}
        for expense in expenses:
            category = expense.get('category', 'Uncategorized')
            amount = expense.get('amount', 0)
            expense_by_category[category] = expense_by_category.get(category, 0) + amount
        
        pie_data = pd.DataFrame({
            'Category': list(expense_by_category.keys()),
            'Amount': list(expense_by_category.values())
        })
        
        # Create pie chart
        fig = px.pie(
            pie_data, 
            values='Amount', 
            names='Category',
            title='Expenses by Category',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig)
        
        # Expenses over time
        if any('date' in expense for expense in expenses):
            expense_by_date = {}
            for expense in expenses:
                if 'date' in expense:
                    date = expense.get('date')
                    amount = expense.get('amount', 0)
                    expense_by_date[date] = expense_by_date.get(date, 0) + amount
            
            time_data = pd.DataFrame({
                'Date': list(expense_by_date.keys()),
                'Amount': list(expense_by_date.values())
            })
            time_data['Date'] = pd.to_datetime(time_data['Date'])
            time_data = time_data.sort_values('Date')
            
            # Create cumulative spending line chart
            time_data['Cumulative'] = time_data['Amount'].cumsum()
            
            fig = px.line(
                time_data, 
                x='Date', 
                y='Cumulative',
                title='Cumulative Spending Over Time',
                labels={'Cumulative': 'Cumulative Spending ($)', 'Date': ''},
                color_discrete_sequence=['#19A7CE']
            )
            
            # Add total budget reference line
            fig.add_hline(
                y=project.get('total_budget', 0),
                line_dash="dash",
                line_color="red",
                annotation_text="Total Budget"
            )
            
            st.plotly_chart(fig)
    else:
        st.info("No expense data available for this project.")
    
    # Assets section
    st.header("Project Assets")
    
    # Fetch assets for this project
    try:
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/assets")
        if response.status_code == 200:
            assets = response.json()
        else:
            assets = []
    except:
        assets = []
    
    if assets:
        # Display assets in expandable sections
        for asset in assets:
            with st.expander(f"{asset.get('name', 'Unnamed Asset')} - {asset.get('progress', 0)}% complete"):
                st.write(f"**Type:** {asset.get('asset_type', 'Unknown')}")
                st.write(f"**Assigned to:** {asset.get('assigned_to', 'Unassigned')}")
                st.write(f"**Status:** {asset.get('status', 'Unknown')}")
                st.write(f"**Due date:** {asset.get('due_date', 'Not set')}")
                st.progress(asset.get('progress', 0) / 100)
    else:
        st.info("No asset data available for this project.")
