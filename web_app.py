# ================= FLASK DAILY WORK UPDATE =================
from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3, hashlib, os
from datetime import datetime

# ================= APP =================
app = Flask(__name__)
DB_NAME = "daily_work.db"

# ================= DATABASE =================
def get_db():
    return sqlite3.connect(DB_NAME)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = get_db()
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

# ================= HTML TEMPLATES =================

LOGIN_HTML = """
<!doctype html>
<html>
<head>
<title>Login - Daily Work Update</title>
<style>
body{font-family:Consolas;background:#0b0f14;color:#c9d1d9;}
input, select{padding:5px;margin:3px;}
button{background:#39ff14;color:#0b0f14;padding:5px 10px;font-weight:bold;}
</style>
</head>
<body>
<h2>Daily Work Update - Login</h2>
<form method="post">
User ID: <input type="text" name="u"><br>
Password: <input type="password" name="p"><br>
<button type="submit">Login</button>
</form>
<p style="color:red;">{{error}}</p>
</body>
</html>
"""

DASH_HTML = """
<!doctype html>
<html>
<head>
<title>Dashboard</title>
<style>
body{font-family:Consolas;background:#0b0f14;color:#c9d1d9;}
table{border-collapse:collapse;width:100%;margin-top:10px;}
th,td{border:1px solid #39ff14;padding:6px;text-align:center;}
th{background:#161b22;color:#39ff14;}
button{padding:4px 8px;margin:2px;background:#39ff14;color:#0b0f14;font-weight:bold;}
</style>
</head>
<body>
<h2>Welcome {{name}} ({{role}})</h2>
<a href="{{url_for('logout')}}">Logout</a>

<h3>Tasks</h3>
<table>
<tr>
<th>ID</th><th>Title</th><th>Model</th><th>Urgency</th><th>Engineer</th><th>Officer</th><th>Technician</th><th>Status</th><th>Progress</th><th>Updated</th><th>Actions</th>
</tr>
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
<td>
{% if role=='officer' %}
<form style="display:inline;" method="post" action="{{url_for('assign_tech', task_id=t[0])}}">
<select name="technician">
<option value="">--Select--</option>
{% for tech in technicians %}
<option value="{{tech}}">{{tech}}</option>
{% endfor %}
</select>
<button type="submit">Assign</button>
</form>
{% endif %}
{% if role=='technician' %}
<form style="display:inline;" method="post" action="{{url_for('update_progress', task_id=t[0])}}">
<input type="number" name="progress" min="0" max="100" value="{{t[8]}}">
<button type="submit">Update</button>
</form>
{% endif %}
</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

# ================= ROUTES =================

@app.route("/", methods=["GET","POST"])
def login():
    error=""
    if request.method=="POST":
        u = request.form.get("u"); p = request.form.get("p")
        if not u or not p:
            error="Fill both fields!"
        else:
            conn = get_db(); cur = conn.cursor()
            cur.execute("SELECT role,name FROM users WHERE username=? AND password_hash=?",
                        (u, hash_pw(p)))
            r = cur.fetchone(); conn.close()
            if r:
                role, name = r
                return redirect(url_for("dashboard", username=u))
            error="Invalid login"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/dashboard/<username>", methods=["GET","POST"])
def dashboard(username):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT role,name FROM users WHERE username=?", (username,))
    r = cur.fetchone()
    if not r: return "User not found"
    role,name = r

    # Get technicians for officer assignment
    cur.execute("SELECT name FROM users WHERE role='technician'")
    technicians = [t[0] for t in cur.fetchall()]

    # Fetch relevant tasks
    cur.execute("SELECT * FROM tasks WHERE engineer=? OR officer=? OR technician=?",
                (name,name,name))
    tasks = cur.fetchall(); conn.close()

    return render_template_string(DASH_HTML, name=name, role=role, tasks=tasks, technicians=technicians)

@app.route("/assign_tech/<int:task_id>", methods=["POST"])
def assign_tech(task_id):
    tech = request.form.get("technician")
    if not tech: return redirect(request.referrer)
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE tasks SET technician=? WHERE id=?", (tech, task_id))
    conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route("/update_progress/<int:task_id>", methods=["POST"])
def update_progress(task_id):
    p = request.form.get("progress")
    try: p=int(p)
    except: p=0
    status = "Completed" if p==100 else "Running"
    now = datetime.now().strftime('%d-%b-%Y %I:%M %p')
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE tasks SET progress=?, status=?, updated_at=? WHERE id=?",
                (p,status,now,task_id))
    conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

# ================= RUN =================
if __name__=="__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
