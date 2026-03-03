import httpx, json
r = httpx.post('http://127.0.0.1:8000/api/auth/login/', json={'username':'admin','password':'admin123'}, timeout=5)
token = r.json().get('token') or r.json().get('access_token')
r2 = httpx.get('http://127.0.0.1:8000/api/interviews/submitted/', headers={'Authorization': f'Bearer {token}'}, timeout=5)
print(f'Status: {r2.status_code}')
data = r2.json()
print(f'Count: {data.get("count")}, Results: {len(data.get("results",[]))}')
for s in data.get('results', []):
    print(f'  ID={s["id"]} contact={s["contact"]["name"]} round={s["round_number"]} answered={s["answered_count"]} completed={s["completed_at"]}')
