#!/usr/bin/env python3
"""
Simple script to test API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_login():
    """Test login and get token"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "email": "admin@tasksphere.com",
        "password": "admin123"
    }
    
    response = requests.post(url, json=data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get('access')
    else:
        print(f"Login failed: {response.text}")
        return None

def test_groups(token):
    """Test groups endpoint"""
    url = f"{BASE_URL}/groups/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Groups Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Groups count: {len(data.get('results', data))}")
        return True
    else:
        print(f"Groups failed: {response.text}")
        return False

def test_swaps(token):
    """Test swaps endpoint"""
    url = f"{BASE_URL}/tasks/swaps/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Swaps Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Swaps count: {len(data.get('results', data))}")
        return True
    else:
        print(f"Swaps failed: {response.text}")
        return False

def test_tasks(token):
    """Test tasks endpoint"""
    url = f"{BASE_URL}/tasks/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Tasks Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Tasks count: {len(data.get('results', data))}")
        return True
    else:
        print(f"Tasks failed: {response.text}")
        return False

def main():
    print("Testing TaskSphere API endpoints...")
    print("=" * 40)
    
    # Test login
    token = test_login()
    if not token:
        print("Cannot proceed without valid token")
        return
    
    print(f"Token received: {token[:20]}...")
    print()
    
    # Test endpoints
    test_groups(token)
    test_swaps(token)
    test_tasks(token)
    
    print("=" * 40)
    print("API test completed!")

if __name__ == "__main__":
    main()
