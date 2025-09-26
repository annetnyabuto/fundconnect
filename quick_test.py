import requests
import json

BASE_URL = "http://127.0.0.1:8080"

# Test 1: Register a user
print("1. Testing user registration...")
user_data = {
    "name": "quicktest",
    "password": "test123",
    "email": "quick@test.com",
    "designation": "Individual"
}

response = requests.post(f"{BASE_URL}/users", json=user_data)
print(f"Registration: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Login
print("\n2. Testing login...")
login_data = {"name": "quicktest", "password": "test123"}
response = requests.post(f"{BASE_URL}/login", json=login_data)
print(f"Login: {response.status_code}")

if response.status_code == 200:
    token = response.json()['token']
    print(f"Token received: {token[:50]}...")
    
    # Test 3: Get campaigns with token
    print("\n3. Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/campaigns", headers=headers)
    print(f"Campaigns: {response.status_code}")
    print(f"Response: {response.json()}")
else:
    print("Login failed!")