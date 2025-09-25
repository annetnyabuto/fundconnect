import requests
import json

BASE_URL = "http://localhost:5000"

def test_user_registration():
    """Test user registration"""
    data = {
        "name": "testuser2",
        "password": "password123",
        "email": "test2@example.com",
        "designation": "Individual"
    }
    response = requests.post(f"{BASE_URL}/users", json=data)
    print(f"Registration: {response.status_code} - {response.json()}")
    return response.status_code == 201

def test_login():
    """Test login and return token"""
    data = {"name": "testuser2", "password": "password123"}
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Login: {response.status_code} - {response.json()}")
    
    if response.status_code == 200:
        return response.json()['token']
    return None

def test_campaigns(token):
    """Test getting campaigns"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/campaigns", headers=headers)
    print(f"Campaigns: {response.status_code} - {response.json()}")

def test_create_campaign(token):
    """Test creating a campaign"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "category": "Education",
        "description": "Test campaign for education",
        "targetamount": 5000
    }
    response = requests.post(f"{BASE_URL}/campaigns", json=data, headers=headers)
    print(f"Create Campaign: {response.status_code} - {response.json()}")
    
    if response.status_code == 201:
        return response.json().get('id')
    return None

def test_make_donation(token, campaign_id):
    """Test making a donation"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Donation",
        "paymentmethod": "Credit Card",
        "amount": 100,
        "campaign_id": campaign_id
    }
    response = requests.post(f"{BASE_URL}/donations", json=data, headers=headers)
    print(f"Make Donation: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    print("Testing FundConnect API...")
    
    # Test registration
    test_user_registration()
    
    # Test login
    token = test_login()
    if not token:
        print("Login failed, stopping tests")
        exit()
    
    # Test campaigns
    test_campaigns(token)
    
    # Test create campaign
    campaign_id = test_create_campaign(token)
    
    # Test donation if campaign was created
    if campaign_id:
        test_make_donation(token, campaign_id)
    
    print("Testing complete!")