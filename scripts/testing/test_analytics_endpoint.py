#!/usr/bin/env python3
"""Test the new contact statistics analytics endpoint"""

import requests

BASE_URL = 'http://127.0.0.1:8000'

response = requests.post(f'{BASE_URL}/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = response.json()['token']

print('Testing new contact statistics endpoint...')
response = requests.get(f'{BASE_URL}/api/contacts/contact-statistics/', headers={'Authorization': f'Bearer {token}'})

if response.status_code == 200:
    data = response.json()
    print('✅ Endpoint works!')
    print('\n📊 Contact Statistics (from ALL contacts in database):')
    print(f'  Total Available Contacts: {data.get("totalAvailableContacts")}')
    print(f'  Total Contacts Attempted: {data.get("totalContactsAttempted")}')
    print(f'  Number of Times Attempted: {data.get("numberOfTimesAttempted")}')
    print(f'  Total Contacts Unattempted: {data.get("totalContactsUnattempted")}')
else:
    print(f'❌ Error: {response.status_code}')
    print(f'Response: {response.text}')
