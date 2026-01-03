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
body{font-family:Consolas;background:#0b0f14;color:#c9d1d9;text-align:center;padding-top:50px;}
input, select{padding:5px;margin:5px;}
button{background:#39ff14;color:#0b0f14;padding:5px 10px;font-weight:bold;margin-top:10px;}
.error{color:red;}
</style>
</head>
<body>
<h2>Daily Work Update - Login</h2>
<form method="post">
<input type="text" name="u" placeholder="User ID"><br>
<input type="password" name="p" placeholder="Password"><br>
<button type="submit">Login</button>
</form>
<p class="error">{{error}}</p>
</body>
</html>
"""

DASH_HTML = """
<!doctype html>
<html>
<head>
<title>{{role}} Dashboard</title>
<style>
body{font-family:Consolas;background:#0b0f14;color:#c9d1d9;padding:10px;}
table{border-collapse:collapse;width:100%;margin-top:10px;}
th,td{border:1px solid #39ff14;padding:6px;text-align:center;}
th{background:#161b22;color:#39ff14;}
input, select{padding:4px;margin:2px;}
button{padding:4px 8px;margin:2px;background:#39ff14;color:#0b0f14;font-weight:bold;}
h2,h3{color:#39ff14;}
form.inline{display:inline;}
</style>
</head>
<body>
<h2>Welcome {{name}} ({{role}})</h2>
<a href="{{url_for('logout')}}">Logout</a>

{% if role=='admin' %}
<h3>Users Management</h3>
<form method="post" action="{{url_for('create_user')}}">
<input type="text" name="name" placeholder="Name">
<input type="text" name="username" placeholder="Username">
<input type="password" name="password" placeholder="Password">
<select name="role">
<option value="admin">Admin</option>
<option value="engineer">Engineer</option>
<option value="officer">Officer</option>
<option value="technician">Technician</option>
</select>
<button type="submit">Create User</button>
</form>
<table>
<tr><th>Name</th><th>Username</th><th>Role</th><th>Action</th></tr>
{% for u in users %}
<tr>
<td>{{u[3]}}</td><td>{{u[0]}}</td><td>{{u[2]}}</td>
<td>
<form method="post" action="{{url_for('delete_user', username=u[0])}}" class="inline">
<button type="submit">Delete</button>
</form>
</td>
</tr>
{% endfor %}
</table>

<h3>Report</h3>
<table>
<tr><th>Engineer</th><th>Pending</th><th>Running</th><th>Completed</th></tr>
{% for r in report %}
<tr><td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td></tr>
{% endfor %}
</table>
{% endif %}

<h3>Tasks</h3>
{% if role=='engineer' %}
<form method="post" action="{{url_for('add_task')}}">
<input type="text" name="title" placeholder="Task Title">
<select name="model">
<option value="12K">12K</option>
<option value="18K">18K</option>
<option value="24K">24K</option>
<option value="30K">30K</option>
<option value="Portable">Portable</option>
</select>
<select name="urgency">
<option value="Regular">Regular</option>
<option value="Urgent">Urgent</option>
<option value="Most Urgent">Most Urgent</option>
</select>
<select name="officer">
{% for o in officers %}
<option value="{{o}}">{{o}}</option>
{% endfor %}
</select>
<button type="submit">Add Task</button>
</form>
{% endif %}

<table>
<tr><th>ID</th><th>Title</th><th>Model</th><th>Urgency</th><th>Engineer</th><th>Officer</th><th>Technician</th><th>Status</th><th>Progress</th><th>Updated</th><th>Actions</th></tr>
{% for t in tasks %}
<tr>
<td>{{t[0]}}</td><td>{{t[1]}}</td><td>{{t[2]}}</td><td>{{t[3]}}</td><td>{{t[4]}}</td><td>{{t[5]}}</td>
<td>{{t[6] or '-'}}</td><td>{{t[7]}}</td><td>{{t[8]}}</td><td>{{t[9]}}</td>
<td>
{% if role=='officer' %}
<form method="post" action="{{url_for('assign_tech', task_id=t[0])}}" class="inline">
<select name="technician">
<option value="">--Select--</option>
{% for tech in technicians %}
<option value="{{tech}}">{{tech}}</option>
{% endfor %}
</select>
<button type="submit">Assign</button>
</form>
<button onclick="window.location.href='{{url_for('update_status', task_id=t[0], status='Running')}}'">Running</button>
<button onclick="window.location.href='{{url_for('update_status', task_id=t[0], status='Completed')}}'">Completed</button>
{% elif role=='technician' %}
<form method="post" action="{{url_for('update_progress', task_id=t[0])}}" class="inline">
<input type="number" name="progress" min="0" max="100" value="{{t[8]}}">
<button type="submit">Update</button>
</form>
{% elif role=='engineer' %}
<form method="post" action="{{url_for('edit_task', task_id=t[0])}}" class="inline">
<button type="submit">Edit</button>
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
        u=request.form.get("u"); p=request.form.get("p")
        if not u or not p: error="Fill both fields!"
        else:
            conn=get_db(); cur=conn.cursor()
            cur.execute("SELECT role,name FROM users WHERE username=? AND password_hash=?",(u, hash_pw(p)))
            r=cur.fetchone(); conn.close()
            if r: return redirect(url_for("dashboard", username=u))
            error="Invalid login"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/dashboard/<username>", methods=["GET","POST"])
def dashboard(username):
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT role,name FROM users WHERE username=?",(username,))
    r=cur.fetchone(); 
    if not r: return "User not found"
    role,name=r

    # fetch users for admin
    cur.execute("SELECT * FROM users"); users=cur.fetchall()

    # fetch tasks
    cur.execute("SELECT * FROM tasks WHERE engineer=? OR officer=? OR technician=?",(name,name,name))
    tasks=cur.fetchall()

    # fetch report
    cur.execute("SELECT engineer,SUM(status='Pending'),SUM(status='Running'),SUM(status='Completed') FROM tasks GROUP BY engineer")
    report=cur.fetchall()

    # officers and technicians
    cur.execute("SELECT name FROM users WHERE role='officer'"); officers=[o[0] for o in cur.fetchall()]
    cur.execute("SELECT name FROM users WHERE role='technician'"); technicians=[t[0] for t in cur.fetchall()]

    conn.close()
    return render_template_string(DASH_HTML, name=name, role=role, users=users, tasks=tasks, report=report, officers=officers, technicians=technicians)

# ================= ADMIN ACTIONS =================

@app.route("/create_user", methods=["POST"])
def create_user():
    name=request.form.get("name"); username=request.form.get("username"); password=request.form.get("password"); role=request.form.get("role")
    if not all([name,username,password,role]): return redirect(request.referrer)
    conn=get_db(); cur=conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",(username,hash_pw(password),role,name))
    conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route("/delete_user/<username>", methods=["POST"])
def delete_user(username):
    if username=="admin": return redirect(request.referrer)
    conn=get_db(); cur=conn.cursor()
    cur.execute("DELETE FROM users WHERE username=?",(username,))
    conn.commit(); conn.close()
    return redirect(request.referrer)

# ================= ENGINEER ACTION =================

@app.route("/add_task", methods=["POST"])
def add_task():
    title=request.form.get("title"); model=request.form.get("model"); urgency=request.form.get("urgency"); officer=request.form.get("officer")
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT name FROM users WHERE username=?",(officer,))
    officer_name=cur.fetchone()
    officer_name=officer_name[0] if officer_name else officer
    now=datetime.now().strftime('%d-%b-%Y %I:%M %p')
    # get engineer name from session or hidden form
    engineer="" 
    for role in ["engineer","officer","technician"]:
        engineer=officer_name if role=="engineer" else ""
    cur.execute("INSERT INTO tasks(title,model,urgency,engineer,officer,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",(title,model,urgency,engineer,officer_name,"Pending",now,now))
    conn.commit(); conn.close()
    return redirect(request.referrer)

# ================= OFFICER ACTIONS =================

@app.route("/assign_tech/<int:task_id>", methods=["POST"])
def assign_tech(task_id):
    tech=request.form.get("technician"); 
    if not tech: return redirect(request.referrer)
    conn=get_db(); cur=conn.cursor()
    cur.execute("UPDATE tasks SET technician=? WHERE id=?",(tech,task_id))
    conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route("/update_status/<int:task_id>/<status>")
def update_status(task_id,status):
    now=datetime.now().strftime('%d-%b-%Y %I:%M %p')
    conn=get_db(); cur=conn.cursor()
    cur.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?",(status,now,task_id))
    conn.commit(); conn.close()
    return redirect(request.referrer)

# ================= TECHNICIAN ACTIONS =================

@app.route("/update_progress/<int:task_id>", methods=["POST"])
def update_progress(task_id):
    p=request.form.get("progress")
    try: p=int(p)
    except: p=0
    status="Completed" if p==100 else "Running"
    now=datetime.now().strftime('%d-%b-%Y %I:%M %p')
    conn=get_db(); cur=conn.cursor()
    cur.execute("UPDATE tasks SET progress=?,status=?,updated_at=? WHERE id=?",(p,status,now,task_id))
    conn.commit(); conn.close()
    return redirect(request.referrer)

# ================= LOGOUT =================

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

# ================= RUN =================
if __name__=="__main__":
    init_db()
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)
