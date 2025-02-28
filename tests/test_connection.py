import requests

# Test API server
print("Testing API server...")
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        print(f"✅ API root endpoint is running.")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ API root endpoint returned error {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ Could not connect to API server: {e}")

print("\nTesting API projects endpoint...")
try:
    response = requests.get("http://localhost:8000/projects/", timeout=5)
    if response.status_code == 200:
        print(f"✅ Projects endpoint is running. Found {len(response.json())} projects.")
    else:
        print(f"❌ Projects endpoint returned error {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ Could not connect to projects endpoint: {e}")

# Test Dashboard
print("\nTesting Streamlit Dashboard...")
try:
    response = requests.get("http://localhost:8501", timeout=5)
    print(f"✅ Streamlit dashboard appears to be running at http://localhost:8501")
except requests.exceptions.RequestException as e:
    print(f"❌ Could not connect to Streamlit dashboard: {e}")

print("\nIf all tests passed, the system is operational!")
print("If any test failed, check that the corresponding server is running.")
