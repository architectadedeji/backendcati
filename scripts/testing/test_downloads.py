import httpx

BASE = "http://127.0.0.1:8000/api"

# Login
r = httpx.post(f"{BASE}/auth/login/", json={"username": "admin", "password": "admin123"}, timeout=5)
token = r.json().get("token") or r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Test summary
print("=== Summary ===")
r = httpx.get(f"{BASE}/analytics/summary/", headers=headers, timeout=5)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(r.json())
else:
    print(r.text[:300])

# Test CSV roster download
print("\n=== CSV Roster ===")
r = httpx.get(f"{BASE}/analytics/enhanced-download/?report=roster&format=csv", headers=headers, timeout=10)
print(f"Status: {r.status_code}, Content-Type: {r.headers.get('content-type')}")
print(f"Size: {len(r.content)} bytes")
lines = r.text.strip().split('\n')
print(f"Lines: {len(lines)} (header + {len(lines)-1} data rows)")
print(f"Header: {lines[0][:200]}")
if len(lines) > 1:
    print(f"Row 1:  {lines[1][:200]}")

# Test XLSX interview summary
print("\n=== XLSX Interview Summary ===")
r = httpx.get(f"{BASE}/analytics/enhanced-download/?report=interview_summary&format=xlsx", headers=headers, timeout=10)
print(f"Status: {r.status_code}, Content-Type: {r.headers.get('content-type')}")
print(f"Size: {len(r.content)} bytes")

# Test CSV detailed
print("\n=== CSV Detailed ===")
r = httpx.get(f"{BASE}/analytics/enhanced-download/?report=detailed&format=csv", headers=headers, timeout=10)
print(f"Status: {r.status_code}, Content-Type: {r.headers.get('content-type')}")
lines = r.text.strip().split('\n')
print(f"Lines: {len(lines)} (header + {len(lines)-1} data rows)")
print(f"Header cols: {len(lines[0].split(','))}")
if len(lines) > 1:
    print(f"Row 1 cols: {len(lines[1].split(','))}")
    print(f"Row 1 preview: {lines[1][:200]}")
else:
    print("No completed interviews to export yet")
