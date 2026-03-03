import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# Find Ruth's interviews
c.execute("SELECT i.id, i.contact_id, i.round_number, i.status, i.completed_at FROM interviews i JOIN contacts ct ON i.contact_id = ct.id WHERE ct.name LIKE '%RUTH%'")
rows = c.fetchall()
print(f"Found {len(rows)} interviews for RUTH:")
for r in rows:
    print(f"  ID={r[0]} contact={r[1]} round={r[2]} status={r[3]} completed={r[4]}")

# Delete responses
c.execute("DELETE FROM responses WHERE interview_id IN (SELECT i.id FROM interviews i JOIN contacts ct ON i.contact_id = ct.id WHERE ct.name LIKE '%RUTH%')")
print(f"  Deleted {c.rowcount} response records")

# Delete interviews
c.execute("DELETE FROM interviews WHERE contact_id IN (SELECT id FROM contacts WHERE name LIKE '%RUTH%')")
print(f"  Deleted {c.rowcount} interview records")

# Reset contact status
c.execute("UPDATE contacts SET status = 'round_1' WHERE name LIKE '%RUTH%'")
print(f"  Reset contact status to round_1")

conn.commit()

# Verify
c.execute("SELECT id, name, status FROM contacts WHERE name LIKE '%RUTH%'")
for r in c.fetchall():
    print(f"Contact: ID={r[0]} name={r[1]} status={r[2]}")
c.execute("SELECT COUNT(*) FROM interviews WHERE contact_id IN (SELECT id FROM contacts WHERE name LIKE '%RUTH%')")
print(f"Remaining interviews: {c.fetchone()[0]}")

conn.close()
print("Done.")
