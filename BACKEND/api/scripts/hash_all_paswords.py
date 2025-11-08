# scripts/hash_all_passwords.py
import MySQLdb
import MySQLdb.cursors

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  

from api.utils.utils_security import make_password  

conn = MySQLdb.connect(host="127.0.0.1", user="tuuser", passwd="tupass", db="tubd", charset="utf8mb4")
cur = conn.cursor(MySQLdb.cursors.DictCursor)

cur.execute("SELECT id, password FROM usuarios")
rows = cur.fetchall()
for r in rows:
    uid = r["id"]
    pw = r["password"] or ""
    if isinstance(pw, str) and pw.startswith("pbkdf2:"):
        print(f"Usuario {uid} ya tiene hash, salteando")
        continue
    if not pw:
        print(f"Usuario {uid} sin password, salteando")
        continue
    new_hash = make_password(pw)
    cur.execute("UPDATE usuarios SET password = %s WHERE id = %s", (new_hash, uid))
    print(f"Hasheado usuario {uid}")

conn.commit()
cur.close()
conn.close()
