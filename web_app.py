from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3, hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "daily-work-secret"
DB = "daily_work.db"

# ================= DB =================
def db():
    return sqlite3.connect(DB)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    c = db(); cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        role TEXT,
        name TEXT
    )""")

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
    )""")

    cur.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",
        ("admin", hash_pw("3624"), "admin", "System Admin"))

    users = [
        ("45213","45213","engineer","Engr. Sadid Hossain"),
        ("41053","41053","engineer","Engr. Enamul Haque"),
        ("38250","38250","officer","Md. Jahid Hasan"),
        ("19359","19359","officer","Papon Chandra Das"),
        ("6810","6810","technician","Selim"),
    ]

    for u,p,r,n in users:
        cur.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",
            (u,hash_pw(p),r,n))

    c.commit(); c.close()

# ================= HTML =================
LOGIN_HTML = """
<!doctype html>
<html>
<head>
<title>Login</title>
<style>
body{background:#0b0f14;color:#39ff14;font-family:Consolas;text-align:center;padding-top:80px;}
input{padding:8px;margin:6px;width:220px;}
button{padding:8px 25px;background:#39ff14;border:none;font-weight:bold;}
</style>
</head>
<body>
<h2>Daily Work Update</h2>
<form method="post">
<input name="u" placeholder="User ID"><br>
<input name="p" type="password" placeholder="Password"><br>
<button>Login</button>
</form>
<p style="color:red">{{error}}</p>
</body>
</html>
"""

DASH_HTML = """
<!doctype html>
<html>
<head>
<title>Dashboard</title>
<style>
body{background:#0b0f14;color:#c9d1d9;font-family:Consolas;padding:15px;}
h2,h3{color:#39ff14}
table{border-collapse:collapse;width:100%;margin-top:10px}
th,td{border:1px solid #39ff14;padding:6px;text-align:center}
th{background:#161b22}
input,select,button{padding:5px;margin:2px}
button{background:#39ff14;border:none;font-weight:bold}
a{color:#39ff14}
</style>
</head>
<body>

<h2>{{name}} ({{role}})</h2>
<a href="/logout">Logout</a>

{% if role=='admin' %}
<h3>User Management</h3>
<form method="post" action="/create_user">
<input name="name" placeholder="Name">
<input name="username" placeholder="Username">
<input name="password" placeholder="Password">
<select name="role">
<option>admin</option>
<option>engineer</option>
<option>officer</option>
<option>technician</option>
</select>
<button>Create</button>
</form>

<table>
<tr><th>Name</th><th>User</th><th>Role</th><th>Action</th></tr>
{% for u in users %}
<tr>
<td>{{u[3]}}</td><td>{{u[0]}}</td><td>{{u[2]}}</td>
<td>
<form method="post" action="/delete_user/{{u[0]}}">
<button>Delete</button>
</form>
</td>
</tr>
{% endfor %}
</table>
{% endif %}

{% if role=='engineer' %}
<h3>Add Task</h3>
<form method="post" action="/add_task">
<input name="title" placeholder="Task Title">
<select name="model">
<option>12K</option><option>18K</option><option>24K</option>
</select>
<select name="urgency">
<option>Regular</option><option>Urgent</option>
</select>
<select name="officer">
{% for o in officers %}<option>{{o}}</option>{% endfor %}
</select>
<button>Add</button>
</form>
{% endif %}

<h3>Tasks</h3>
<table>
<tr>
<th>ID</th><th>Title</th><th>Model</th><th>Urgency</th>
<th>Engineer</th><th>Officer</th><th>Technician</th>
<th>Status</th><th>Progress</th><th>Action</th>
</tr>

{% for t in tasks %}
<tr>
<td>{{t[0]}}</td><td>{{t[1]}}</td><td>{{t[2]}}</td><td>{{t[3]}}</td>
<td>{{t[4]}}</td><td>{{t[5]}}</td><td>{{t[6] or '-'}}</td>
<td>{{t[7]}}</td><td>{{t[8]}}%</td>
<td>

{% if role=='officer' %}
<form method="post" action="/assign_tech/{{t[0]}}">
<select name="technician">
{% for tech in technicians %}<option>{{tech}}</option>{% endfor %}
</select>
<button>Assign</button>
</form>
<a href="/update_status/{{t[0]}}/Running">Running</a>
<a href="/update_status/{{t[0]}}/Completed">Done</a>

{% elif role=='technician' %}
<form method="post" action="/update_progress/{{t[0]}}">
<input name="progress" type="number" value="{{t[8]}}" min="0" max="100">
<button>Update</button>
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
    err=""
    if request.method=="POST":
        u,p=request.form["u"],request.form["p"]
        c=db();cur=c.cursor()
        cur.execute("SELECT role,name FROM users WHERE username=? AND password_hash=?",(u,hash_pw(p)))
        r=cur.fetchone();c.close()
        if r:
            session["u"]=u;session["r"]=r[0];session["n"]=r[1]
            return redirect("/dashboard")
        err="Invalid Login"
    return render_template_string(LOGIN_HTML,error=err)

@app.route("/dashboard")
def dashboard():
    if "u" not in session: return redirect("/")
    r,n=session["r"],session["n"]
    c=db();cur=c.cursor()

    if r=="admin": cur.execute("SELECT * FROM tasks")
    else: cur.execute("SELECT * FROM tasks WHERE engineer=? OR officer=? OR technician=?",(n,n,n))
    tasks=cur.fetchall()

    cur.execute("SELECT * FROM users"); users=cur.fetchall()
    cur.execute("SELECT name FROM users WHERE role='officer'"); officers=[i[0] for i in cur.fetchall()]
    cur.execute("SELECT name FROM users WHERE role='technician'"); technicians=[i[0] for i in cur.fetchall()]
    c.close()

    return render_template_string(DASH_HTML,role=r,name=n,users=users,tasks=tasks,officers=officers,technicians=technicians)

@app.route("/add_task",methods=["POST"])
def add_task():
    if session["r"]!="engineer": return redirect("/dashboard")
    now=datetime.now().strftime("%d-%b-%Y %I:%M %p")
    c=db();cur=c.cursor()
    cur.execute("""
    INSERT INTO tasks(title,model,urgency,engineer,officer,status,created_at,updated_at)
    VALUES (?,?,?,?,?,?,?,?)
    """,(request.form["title"],request.form["model"],request.form["urgency"],
         session["n"],request.form["officer"],"Pending",now,now))
    c.commit();c.close()
    return redirect("/dashboard")

@app.route("/assign_tech/<int:i>",methods=["POST"])
def assign_tech(i):
    c=db();cur=c.cursor()
    cur.execute("UPDATE tasks SET technician=? WHERE id=?",(request.form["technician"],i))
    c.commit();c.close()
    return redirect("/dashboard")

@app.route("/update_status/<int:i>/<s>")
def update_status(i,s):
    c=db();cur=c.cursor()
    cur.execute("UPDATE tasks SET status=? WHERE id=?",(s,i))
    c.commit();c.close()
    return redirect("/dashboard")

@app.route("/update_progress/<int:i>",methods=["POST"])
def update_progress(i):
    p=int(request.form["progress"])
    s="Completed" if p==100 else "Running"
    c=db();cur=c.cursor()
    cur.execute("UPDATE tasks SET progress=?,status=? WHERE id=?",(p,s,i))
    c.commit();c.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    init_db()
    app.run(debug=True)
