from flask import Flask, render_template_string, request
import sqlite3, hashlib
import os

app = Flask(__name__)
DB = "daily_work.db"

def db():
    return sqlite3.connect(DB)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        role TEXT,
        name TEXT
    )
    """)
    cur.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",
                ("admin", hash_pw("3624"), "admin", "System Admin"))
    conn.commit()
    conn.close()

LOGIN_HTML = """<html> ... </html>"""  # Simple HTML Login page

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form.get("u")
        p=request.form.get("p")
        if not u or not p: return "Fill both fields!"
        con=db(); cur=con.cursor()
        cur.execute("SELECT role,name FROM users WHERE username=? AND password_hash=?",
                    (u,hash_pw(p)))
        r=cur.fetchone(); con.close()
        if r: return f"Login OK - User: {r[1]} | Role: {r[0]}"
        return "Invalid Login"
    return render_template_string(LOGIN_HTML)

if __name__=="__main__":
    if not os.path.exists(DB):
        init_db()
    app.run()
