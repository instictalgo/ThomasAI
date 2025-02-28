import streamlit as st
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")
print(f"Streamlit version: {st.__version__}")
st.title("Thomas AI Test Page")
st.write("If you can see this, Streamlit is working!")
