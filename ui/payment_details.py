import streamlit as st
import requests
import pandas as pd
import sys
import os
from datetime import datetime

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API URL
API_BASE_URL = "http://localhost:8002"

def get_payment_method_icon(method):
    """Return the appropriate payment method icon"""
    if "paypal" in method.lower():
        return "https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg"
    elif "crypto" in method.lower() or "sol" in method.lower():
        return "https://cryptologos.cc/logos/solana-sol-logo.png"
    elif "bank" in method.lower():
        return "https://cdn-icons-png.flaticon.com/512/2830/2830284.png"
    else:
        return "https://cdn-icons-png.flaticon.com/512/1019/1019607.png"

def display_payment_details():
    st.title("Payment Details")
    
    # Get all employees
    try:
        response = requests.get(f"{API_BASE_URL}/payments/employees")
        if response.status_code == 200:
            employees = response.json()
        else:
            st.error("Failed to fetch employees")
            return
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return
    
    # Employee selection
    selected_employee = st.selectbox("Select Employee", employees)
    
    if selected_employee:
        # Get payments for selected employee
        try:
            response = requests.get(f"{API_BASE_URL}/payments/employee/{selected_employee}")
            if response.status_code == 200:
                payments = response.json()
            else:
                st.error("Failed to fetch payments for employee")
                return
        except Exception as e:
            st.error(f"Error connecting to API: {str(e)}")
            return
        
        # Display employee info
        st.header(f"Payments for {selected_employee}")
        
        # Calculate total payments
        if payments:
            total_usd = sum(p["amount"] for p in payments if p["currency"] == "USD")
            total_sol = sum(p["amount"] for p in payments if p["currency"] == "SOL")
            
            # Display totals
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total USD Payments", f"${total_usd:,.2f}")
            with col2:
                st.metric("Total SOL Payments", f"{total_sol:,.2f} SOL")
            
            # Display payment history
            st.subheader("Payment History")
            
            # Create expandable sections for each payment
            for payment in sorted(payments, key=lambda x: x.get("created_at", ""), reverse=True):
                with st.expander(f"Payment on {payment.get('created_at', 'Unknown Date')} - {payment.get('currency')} {payment.get('amount')}"):
                    cols = st.columns([1, 3])
                    
                    # Payment method icon
                    with cols[0]:
                        st.image(get_payment_method_icon(payment.get("payment_method", "")), width=100)
                    
                    # Payment details
                    with cols[1]:
                        st.write(f"**Amount:** {payment.get('currency')} {payment.get('amount')}")
                        st.write(f"**Method:** {payment.get('payment_method', 'Unknown')}")
                        st.write(f"**Status:** {payment.get('status', 'Unknown')}")
                        st.write(f"**Transaction ID:** {payment.get('transaction_id', 'N/A')}")
                        
                        # Add payment link if available
                        if payment.get("payment_link"):
                            st.write(f"**Payment Link:** [View Transaction]({payment.get('payment_link')})")
        else:
            st.info(f"No payments found for {selected_employee}")

if __name__ == "__main__":
    display_payment_details() 