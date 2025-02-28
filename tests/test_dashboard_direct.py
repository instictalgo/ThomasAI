import streamlit as st
import sys
import os

# Print debug info
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Streamlit version: {st.__version__}")

st.title("Thomas AI Direct Test")
st.write("This is a direct test of the Streamlit dashboard.")

# Add a simple test that doesn't rely on any API
if st.button("Test Local Function"):
    st.success("Local function works!")
