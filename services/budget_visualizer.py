import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class BudgetVisualizer:
    def __init__(self):
        pass
    
    def create_budget_overview(self, project_name, total_budget, total_spent, remaining):
        """Create a gauge chart for budget overview"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_spent,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"Budget Usage for {project_name}"},
            delta={"reference": total_budget, "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
            gauge={
                "axis": {"range": [0, total_budget], "tickwidth": 1, "tickcolor": "darkblue"},
                "bar": {"color": "darkblue"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, total_budget * 0.7], "color": "green"},
                    {"range": [total_budget * 0.7, total_budget * 0.9], "color": "yellow"},
                    {"range": [total_budget * 0.9, total_budget], "color": "red"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": total_budget
                }
            }
        ))
        
        return fig
    
    def create_category_breakdown(self, categories):
        """Create a pie chart of expenses by category"""
        df = pd.DataFrame({
            'Category': list(categories.keys()),
            'Amount': list(categories.values())
        })
        fig = px.pie(df, values='Amount', names='Category', 
                    title='Expense Distribution by Category')
        return fig
    
    def create_expense_timeline(self, expenses, start_date, end_date):
        """Create a line chart of expenses over time"""
        # Convert to DataFrame
        df = pd.DataFrame(expenses)
        
        # Ensure dates are parsed correctly
        df['date'] = pd.to_datetime(df['date'])
        
        # Group by date and sum amounts
        daily_expenses = df.groupby('date')['amount'].sum().reset_index()
        
        # Create a date range for the full project duration
        date_range = pd.date_range(start=start_date, end=end_date)
        full_range_df = pd.DataFrame({'date': date_range})
        
        # Merge with actual expenses to include days with zero expenses
        merged_df = pd.merge(full_range_df, daily_expenses, on='date', how='left').fillna(0)
        
        # Calculate cumulative spending
        merged_df['cumulative'] = merged_df['amount'].cumsum()
        
        # Create the figure
        fig = go.Figure()
        
        # Add daily expenses as bars
        fig.add_trace(go.Bar(
            x=merged_df['date'],
            y=merged_df['amount'],
            name='Daily Expenses'
        ))
        
        # Add cumulative spending as a line
        fig.add_trace(go.Scatter(
            x=merged_df['date'],
            y=merged_df['cumulative'],
            name='Cumulative Spending',
            line=dict(color='red', width=2)
        ))
        
        # Update layout
        fig.update_layout(
            title='Expense Timeline',
            xaxis_title='Date',
            yaxis_title='Amount',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_budget_forecast(self, current_date, end_date, total_budget, spent_to_date, burn_rate):
        """Create a forecast of budget spending based on current burn rate"""
        # Calculate days remaining
        current_date = pd.to_datetime(current_date)
        end_date = pd.to_datetime(end_date)
        days_total = (end_date - pd.to_datetime(current_date)).days
        
        if days_total <= 0:
            return None  # Project already ended
        
        # Calculate daily burn rate (average daily spending)
        days_elapsed = (current_date - pd.to_datetime(current_date)).days or 1  # Avoid division by zero
        
        # Create date range for forecast
        date_range = pd.date_range(start=current_date, end=end_date)
        forecast_df = pd.DataFrame({'date': date_range})
        
        # Calculate projected spending
        forecast_df['projected_daily'] = burn_rate
        forecast_df['projected_cumulative'] = spent_to_date + forecast_df.index * burn_rate
        
        # Add ideal spending line (linear from 0 to total budget)
        forecast_df['ideal_cumulative'] = total_budget * (
            (forecast_df.index + days_elapsed) / (days_total + days_elapsed)
        )
        
        # Create the figure
        fig = go.Figure()
        
        # Add projected cumulative spending
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['projected_cumulative'],
            name='Projected Spending',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Add ideal spending line
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['ideal_cumulative'],
            name='Ideal Spending',
            line=dict(color='green', width=2)
        ))
        
        # Add budget limit line
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=[total_budget] * len(forecast_df),
            name='Budget Limit',
            line=dict(color='black', width=1, dash='dot')
        ))
        
        # Calculate projected completion date (when spending hits budget)
        days_to_budget = (total_budget - spent_to_date) / burn_rate if burn_rate > 0 else days_total
        projected_completion = current_date + timedelta(days=days_to_budget)
        
        # Add projected completion marker if it falls within project timeframe
        if projected_completion <= end_date and burn_rate > 0:
            fig.add_vline(
                x=projected_completion, 
                line_width=2, 
                line_dash="dash", 
                line_color="red",
                annotation_text="Projected Budget Exhaustion", 
                annotation_position="top right"
            )
        
        # Update layout
        fig.update_layout(
            title='Budget Forecast',
            xaxis_title='Date',
            yaxis_title='Cumulative Amount',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig 