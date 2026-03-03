"""Test that interview responses are properly stored in the database."""
import httpx
import json

BASE = "http://127.0.0.1:8000/api"

# Login
r = httpx.post(f"{BASE}/auth/login/", json={"username": "admin", "password": "admin123"}, timeout=5)
token = r.json().get("token") or r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("=== TEST 1: xform-submit stores form_data correctly ===")
# Start an interview for contact 6, round 1
r = httpx.post(f"{BASE}/interviews/contact/6/round/1/start/", headers=headers, timeout=5)
print(f"Start interview: {r.status_code}")

if r.status_code in (200, 201):
    interview = r.json()
    interview_id = interview["id"]
    print(f"Interview ID: {interview_id}")
    
    # Submit form data (mimicking what frontend sends)
    test_form_data = {
        "form_data": {
            "_1a_Start_date_and_time": "2026-02-22T14:00",
            "_1b_Name_of_Customer": "Test Name",
            "Before_I_proceed_I_will_need_": "yes",
            "May_I_proceed_with_the_survey_": "yes"
        }
    }
    
    r2 = httpx.post(f"{BASE}/interviews/{interview_id}/xform-submit/", json=test_form_data, headers=headers, timeout=5)
    print(f"Submit response: {r2.status_code} - {r2.text}")
    
    # Now fetch the interview and check xform_data
    r3 = httpx.get(f"{BASE}/interviews/{interview_id}/", headers=headers, timeout=5)
    if r3.status_code == 200:
        data = r3.json()
        xform = data.get("xform_data")
        print(f"\nStored xform_data type: {type(xform).__name__}")
        if xform:
            print(f"Keys: {list(xform.keys())}")
            # Check it's NOT wrapped in form_data
            if "form_data" in xform and len(xform) == 1:
                print("FAIL: Still wrapped in form_data!")
            else:
                print("PASS: Form data stored directly (unwrapped)")
        else:
            print("FAIL: xform_data is None!")
    else:
        print(f"Get interview failed: {r3.status_code} - {r3.text}")
else:
    print(f"Could not start interview: {r.text[:300]}")

print("\n=== TEST 2: PATCH saves xform_data (save progress) ===")
# Start another interview  
r = httpx.post(f"{BASE}/interviews/contact/8/round/1/start/", headers=headers, timeout=5)
print(f"Start interview: {r.status_code}")

if r.status_code in (200, 201):
    interview = r.json()
    interview_id = interview["id"]
    
    # Save progress via PATCH
    progress_data = {
        "xform_data": {"_1a_Start_date_and_time": "2026-02-22T14:00", "partial": True},
        "status": "in_progress"
    }
    r2 = httpx.patch(f"{BASE}/interviews/{interview_id}/", json=progress_data, headers=headers, timeout=5)
    print(f"Save progress: {r2.status_code}")
    
    if r2.status_code == 200:
        data = r2.json()
        xform = data.get("xform_data")
        if xform and "_1a_Start_date_and_time" in xform:
            print("PASS: Progress data saved via PATCH")
        else:
            print(f"FAIL: xform_data not in response: {xform}")
    else:
        print(f"FAIL: {r2.text[:300]}")
else:
    print(f"Could not start interview: {r.text[:300]}")

print("\n=== TEST 3: Verify DB directly ===")
import sqlite3
conn = sqlite3.connect("db.sqlite3")
c = conn.cursor()
c.execute("SELECT id, contact_id, round_number, status, xform_data, completed_at FROM interviews WHERE xform_data IS NOT NULL")
rows = c.fetchall()
print(f"Interviews with xform_data: {len(rows)}")
for row in rows:
    data = json.loads(row[4]) if isinstance(row[4], str) else row[4]
    has_wrapper = isinstance(data, dict) and "form_data" in data and len(data) <= 3
    print(f"  ID={row[0]} contact={row[1]} round={row[2]} status={row[3]} completed={row[5]}")
    print(f"    Fields: {len(data) if isinstance(data, dict) else '?'}, has_wrapper={has_wrapper}")
conn.close()
