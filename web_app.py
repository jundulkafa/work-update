# ================= FLASK DAILY WORK UPDATE =================
from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3, hashlib, os
from datetime import datetime

# ================= APP =================
app = Flask(__name__)
DB = "daily_work.db"

# ================= DATABASE =================
def db():
    return sqlite3.connect(DB)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = db()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        role TEXT,
        name TEXT
    )
    """)

    # Tasks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        model TEXT,
        urgency TEXT,
        engineer TEXT,
        officer TEXT,
        technician TEXT,
        status TEXT,
        progress INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # Default admin
    cur.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",
                ("admin", hash_pw("3624"), "admin", "System Admin"))

    # Default users
    defaults = [
        ("45213","45213","engineer","Engr. Sadid Hossain - 45213"),
        ("41053","41053","engineer","Engr. Enamul Haque - 41053"),
        ("38250","38250","officer","Md. Jahid Hasan - 38250"),
        ("19359","19359","officer","Papon Chandra Das - 19359"),
        ("6810","6810","technician","Selim - 6810"),
    ]

    for u,p,r,n in defaults:
        cur.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",
                    (u, hash_pw(p), r, n))

    conn.commit()
    conn.close()

# ================= HTML =================
LOGIN_HTML = """
<!doctype html>
<html>
<head><title>Login</title></head>
<body>
<h2>Daily Work Update - Login</h2>
<form method="post">
User ID: <input type="text" name="u"><br><br>
Password: <input type="password" name="p"><br><br>
<input type="submit" value="Login">
</form>
</body>
</html>
"""

DASH_HTML = """
<!doctype html>
<html>
<head><title>Dashboard</title></head>
<body>
<h2>Welcome {{name}} ({{role}})</h2>
<p>Tasks:</p>
<table border="1">
<tr><th>ID</th><th>Title</th><th>Model</th><th>Urgency</th><th>Engineer</th><th>Officer</th><th>Technician</th><th>Status</th><th>Progress</th><th>Updated</th></tr>
{% for t in tasks %}
<tr>
<td>{{t[0]}}</td>
<td>{{t[1]}}</td>
<td>{{t[2]}}</td>
<td>{{t[3]}}</td>
<td>{{t[4]}}</td>
<td>{{t[5]}}</td>
<td>{{t[6] or "-"}}</td>
<td>{{t[7]}}</td>
<td>{{t[8]}}</td>
<td>{{t[9]}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

# ================= ROUTES =================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = request.form.get("u")
        p = request.form.get("p")
        if not u or not p: return "Fill both fields!"
        con = db(); cur = con.cursor()
        cur.execute("SELECT role,name FROM users WHERE username=? AND password_hash=?",
                    (u, hash_pw(p)))
        r = cur.fetchone(); con.close()
        if r:
            role, name = r
            return redirect(url_for("dashboard", username=u))
        return "Invalid Login"
    return render_template_string(LOGIN_HTML)

@app.route("/dashboard/<username>")
def dashboard(username):
    con = db(); cur = con.cursor()
    cur.execute("SELECT role,name FROM users WHERE username=?", (username,))
    r = cur.fetchone()
    if not r: return "User not found"
    role,name = r

    cur.execute("SELECT * FROM tasks WHERE engineer=? OR officer=? OR technician=?",
                (name,name,name))
    tasks = cur.fetchall()
    con.close()
    return render_template_string(DASH_HTML, name=name, role=role, tasks=tasks)

# ================= RUN =================
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
