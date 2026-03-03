#!/usr/bin/env python3
"""Test API endpoint directly with authentication"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Get bearer token by logging in"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"Login response: {data}")
        # Handle both 'access_token' and 'token' keys
        token = data.get("access_token") or data.get("token")
        if token:
            print(f"✅ Login successful, token: {token[:20]}...")
            return token
        else:
            print(f"❌ No token in response: {data}")
            return None
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_get_contacts(token):
    """Get list of contacts"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/contacts/", headers=headers)
    
    print(f"\n📍 API Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response data: {data}")
        
        # Handle pagination response
        if isinstance(data, dict) and "results" in data:
            contacts = data["results"]
            total = data.get("count", len(contacts))
            print(f"✅ API returned contacts successfully")
            print(f"📊 Total: {total}")
            print(f"\n📋 Contacts:")
            for contact in contacts:
                print(f"  - ID: {contact['id']}, Name: {contact['name']}, Serial: {contact['serial_number']}, Location: {contact['location']}")
        else:
            print(f"Got response: {data}")
    elif response.status_code == 500:
        print(f"❌ API Error: 500 - Internal Server Error")
        try:
            print(f"Response body: {response.json()}")
        except:
            print(f"Response text: {response.text}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    token = test_login()
    if token:
        test_get_contacts(token)
    else:
        print("Cannot test contacts without token")
        sys.exit(1)
