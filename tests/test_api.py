import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    print("Test 1: Registering a new user...")
    payload = {
        "username": "tiana_test",
        "password": "secret123",
        "full_name": "Tiana Test",
        "team": "Retention Team",
        "role": "Test Analyst"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        if response.status_code == 200:
            user = response.json()
            print(f"User created! ID: {user['id']}")
            print(f"Name: {user['full_name']}, Team: {user['team']}")
            return True
        else:
            print(f"Registration failed: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"Network error: {e}")
        return False

def test_login():
    print("\nTest 2: Logging in...")
    payload = {
        "username": "tiana_test",
        "password": "secret123"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("Login successful! Token received")
            return token
        else:
            print(f"Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"Network error: {e}")
        return None

# def test_profile(token):
#     print("\nTest 3: Fetching user profile...")
#     try:
#         headers = {"Authorization": f"Bearer {token}"}
#         response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
#         if response.status_code == 200:
#             profile = response.json()
#             print("Profile retrieved!")
#             print(f"   Username: {profile['username']}")
#             print(f"   Name: {profile['full_name']}")
#             print(f"   Team: {profile['team']}")
#             print(f"   Role: {profile['role']}")
#             print(f"   Joined on: {profile['joined_date']}")
#             print(f"   Active: {'Yes' if profile['is_active'] else 'No'}")
#         else:
#             print(f"Profile fetch failed: {response.json()}")
#     except Exception as e:
#         print(f"Network error: {e}")

def test_login_fail():
    print("\nTest 4: Trying to login with wrong password...")
    payload = {
        "username": "tiana_test",
        "password": "wrongpassword"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        if response.status_code == 401:
            print("Expected failure: incorrect password")
        else:
            print(f"Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")