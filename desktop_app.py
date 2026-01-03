import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, hashlib, os
from datetime import datetime
# ================= UTIL =================
def wrap_text(text, max_len=35):
    if not text:
        return ""
    words = text.split()
    lines = []
    line = ""

    for w in words:
        if len(line) + len(w) <= max_len:
            line += w + " "
        else:
            lines.append(line.strip())
            line = w + " "

    lines.append(line.strip())
    return "\n".join(lines)


DB_NAME = "daily_work.db"

# ================= DATABASE =================

def get_db():
    return sqlite3.connect(DB_NAME)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = get_db()
    cur = conn.cursor()

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
        start_time TEXT,
        created_at TEXT,
        updated_at TEXT
    )""")

    if not cur.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        cur.execute(
            "INSERT INTO users VALUES (?,?,?,?)",
            ("admin", hash_password("3624"), "admin", "System Admin")
        )

    defaults = [
        ("45213","45213","engineer","Engr. Sadid Hossain - 45213 "),
        ("41053","41053","engineer","Engr. Enamul Haque - 41053 "),
        ("38250","38250","officer","Md. Jahid Hasan - 38250 "),
        ("19359","19359","officer","Papon Chandra Das - 19359 "),
        ("6810","6810","technician","Selim - 6810"),
    ]

    for u,p,r,n in defaults:
        if not cur.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            cur.execute(
                "INSERT INTO users VALUES (?,?,?,?)",
                (u, hash_password(p), r, n)
            )

    conn.commit()
    conn.close()

# ================= UTIL =================

def safe_icon(win, icon="icon.ico"):
    try:
        if os.path.exists(icon):
            win.iconbitmap(icon)
    except:
        pass

def apply_hacker_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    bg="#0b0f14"; fg="#c9d1d9"; neon="#39ff14"; dark="#161b22"
    root.configure(bg=bg)
    style.configure(".", background=bg, foreground=fg, fieldbackground=dark)
    style.configure("TLabel", font=("Consolas",10))
    style.configure("TButton", foreground=neon, font=("Consolas",10,"bold"))
    style.configure("Treeview", background=dark, rowheight=32)
    style.configure("Treeview.Heading", foreground=neon)

def logout(root, login_win):
    if messagebox.askyesno("Logout","Do you want to logout?"):
        root.destroy()
        login_win.deiconify()

# ================= THEME =================

def apply_hacker_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    bg="#0b0f14"; fg="#c9d1d9"; neon="#39ff14"; dark="#161b22"
    root.configure(bg=bg)

    style.configure(".", background=bg, foreground=fg, fieldbackground=dark)
    style.configure("TLabel", font=("Consolas",10))
    style.configure("TButton", foreground=neon, font=("Consolas",10,"bold"))
    style.configure("Glow.TButton", foreground=bg, background=neon)
    style.configure("Treeview", background=dark, rowheight=34)
    style.configure("Treeview.Heading", foreground=neon)
    style.map("Treeview", background=[("selected","#238636")])
    # ===== ADMIN NOTEBOOK COLOR FIX =====
    style.configure(
        "TNotebook",
        background=bg,
        borderwidth=0
    )

    style.configure(
        "TNotebook.Tab",
        background=dark,
        foreground=fg,
        padding=(14,6),
        font=("Consolas",10,"bold")
    )

    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", neon),
            ("active", "#1f6feb")
        ],
        foreground=[
            ("selected", bg),
            ("active", "#ffffff")
        ]
    )



def glow(btn):
    btn.bind("<Enter>", lambda e: btn.configure(style="Glow.TButton"))
    btn.bind("<Leave>", lambda e: btn.configure(style="TButton"))


# ================= LOGOUT =================

def logout(root, login_win):
    if messagebox.askyesno("Logout","Do you want to logout?"):
        root.destroy()
        login_win.deiconify()


# ================= ENGINEER PANEL =================

class EngineerPanel(ttk.Frame):
    def __init__(self, parent, root, login_win, username):
        super().__init__(parent)
        self.root = root
        self.login_win = login_win
        self.username = username

        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE username=?", (username,))
        self.name = cur.fetchone()[0]
        conn.close()

        self.editing_task_id = None

        self.pack(fill="both", expand=True)
        self.ui()

    def ui(self):
        # -------- TOP BAR --------
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10)

        ttk.Label(
            top,
            text=f"ENGINEER PANEL – {self.name} ({self.username})",
            font=("Consolas", 14, "bold"),
            foreground="#39ff14"
        ).pack(side="left")

        b = ttk.Button(
            top, text="LOGOUT",
            command=lambda: logout(self.root, self.login_win)
        )
        b.pack(side="right")
        glow(b)

        # -------- TASK ENTRY --------
        entry = ttk.LabelFrame(self, text="Add / Edit Task", padding=10)
        entry.pack(fill="x", padx=10, pady=10)

        self.title = ttk.Entry(entry, width=35)
        self.model = ttk.Combobox(
            entry,
            values=["12K", "18K", "24K", "30K", "Portable"],
            state="readonly",
            width=15
        )
        self.urgency = ttk.Combobox(
            entry,
            values=["Regular", "Urgent", "Most Urgent"],
            state="readonly",
            width=14
        )
        self.officer = ttk.Combobox(
            entry,
            values=["Md. Jahid Hasan", "Papon Chandra Das"],
            state="readonly",
            width=20
        )

        fields = [
            ("Task", self.title),
            ("Model", self.model),
            ("Urgency", self.urgency),
            ("Officer", self.officer)
        ]

        for i, (l, w) in enumerate(fields):
            ttk.Label(entry, text=l).grid(row=0, column=i * 2)
            w.grid(row=0, column=i * 2 + 1, padx=4)

        self.add_btn = ttk.Button(entry, text="ADD TASK", command=self.add_or_update_task)
        self.add_btn.grid(row=0, column=8, padx=10)
        glow(self.add_btn)

        # -------- TASK LIST --------
        self.tree = ttk.Treeview(
            self,
            columns=("id", "details", "model", "urgency", "officer", "status", "time"),
            show="headings"
        )

        heads = ["ID", "TASK DETAILS", "MODEL", "URGENCY", "OFFICER", "STATUS", "TIME"]
        for i, c in enumerate(self.tree["columns"]):
            self.tree.heading(c, text=heads[i], anchor="center")
            self.tree.column(c, width=70, anchor="center")

        self.tree.column("details", width=350)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # -------- EDIT BUTTON --------
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        edit_btn = ttk.Button(btn_frame, text="EDIT TASK", command=self.load_for_edit)
        edit_btn.pack()
        glow(edit_btn)

        self.load()

    # -------- ADD / UPDATE TASK --------
    def add_or_update_task(self):
        if not all([
            self.title.get(),
            self.model.get(),
            self.urgency.get(),
            self.officer.get()
        ]):
            messagebox.showwarning("Missing", "Fill all fields")
            return

        now = datetime.now().strftime('%d-%b-%Y %I:%M %p')
        conn = get_db(); cur = conn.cursor()

        if self.editing_task_id:
            cur.execute("""
                UPDATE tasks SET
                title=?, model=?, urgency=?, officer=?, updated_at=?
                WHERE id=?
            """, (
                self.title.get(),
                self.model.get(),
                self.urgency.get(),
                self.officer.get(),
                now,
                self.editing_task_id
            ))
            self.editing_task_id = None
            self.add_btn.config(text="ADD TASK")
            messagebox.showinfo("Updated", "Task updated successfully")
        else:
            cur.execute("""
                INSERT INTO tasks
                (title, model, urgency, engineer, officer, status, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                self.title.get(),
                self.model.get(),
                self.urgency.get(),
                self.name,
                self.officer.get(),
                "Pending",
                now,
                now
            ))

        conn.commit(); conn.close()
        self.clear_fields()
        self.load()

    # -------- LOAD TASK FOR EDIT --------
    def load_for_edit(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Task", "Select a task to edit")
            return

        values = self.tree.item(selected, "values")
        self.editing_task_id = values[0]

        self.title.delete(0, "end")
        self.title.insert(0, values[1])
        self.model.set(values[2])
        self.urgency.set(values[3])
        self.officer.set(values[4])

        self.add_btn.config(text="UPDATE TASK")

    # -------- LOAD TASK LIST --------
    def load(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db(); cur = conn.cursor()
        cur.execute("""
            SELECT id, title, model, urgency, officer, status, updated_at
            FROM tasks WHERE engineer=?
        """, (self.name,))
        for r in cur.fetchall():
            self.tree.insert(
                "",
                "end",
                values=(r[0], wrap_text(r[1]), r[2], r[3], r[4], r[5], r[6])
            )
        conn.close()

    def clear_fields(self):
        self.title.delete(0, "end")
        self.model.set("")
        self.urgency.set("")
        self.officer.set("")
# ================= TECHNICIAN PANEL =================

class TechnicianPanel(ttk.Frame):
    def __init__(self,parent,root,login_win,username):
        super().__init__(parent)
        self.root=root
        self.login_win=login_win
        self.username=username

        conn=get_db();cur=conn.cursor()
        cur.execute("SELECT name FROM users WHERE username=?", (username,))
        self.name=cur.fetchone()[0]
        conn.close()

        self.pack(fill="both",expand=True)
        self.ui()

    def ui(self):
        top=ttk.Frame(self); top.pack(fill="x",padx=10)
        ttk.Label(top,text=f"TECHNICIAN PANEL – {self.name}",
                  font=("Consolas",14,"bold"),foreground="#39ff14").pack(side="left")
        ttk.Button(top,text="LOGOUT",
                   command=lambda:logout(self.root,self.login_win)).pack(side="right")

        self.tree=ttk.Treeview(
            self,
            columns=("id","title","engineer","status","progress"),
            show="headings"
        )
        for c in self.tree["columns"]:
            self.tree.heading(c,text=c.upper())
            self.tree.column(c,width=180)
        self.tree.pack(fill="both",expand=True,padx=10,pady=10)

        self.scale=ttk.Scale(self,from_=0,to=100,orient="horizontal")
        self.scale.pack(pady=5)

        ttk.Button(self,text="UPDATE PROGRESS",
                   command=self.update_progress).pack()

        self.load()

    def load(self):
        self.tree.delete(*self.tree.get_children())
        conn=get_db();cur=conn.cursor()
        cur.execute("""
            SELECT id,title,engineer,status,progress
            FROM tasks WHERE technician=?
        """,(self.name,))
        for r in cur.fetchall():
            self.tree.insert("", "end", values=r)
        conn.close()

    def update_progress(self):
        sel=self.tree.selection()
        if not sel: return
        tid=self.tree.item(sel[0])["values"][0]
        p=int(self.scale.get())
        conn=get_db();cur=conn.cursor()
        cur.execute(
            "UPDATE tasks SET progress=?,status=? WHERE id=?",
            (p,"Completed" if p==100 else "Running",tid)
        )
        conn.commit();conn.close()
        self.load()


# ================= OFFICER PANEL =================

class OfficerPanel(ttk.Frame):
    def __init__(self, parent, root, login_win, username):
        super().__init__(parent)
        self.root = root
        self.login_win = login_win
        self.username = username

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE username=?", (username,))
        self.name = cur.fetchone()[0]
        conn.close()

        self.pack(fill="both", expand=True)
        self.ui()
        self.auto_refresh()   # 🔥 live refresh

    # ---------------- UI ----------------
    def ui(self):
        # ---- TOP BAR ----
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(
            top,
            text=f"OFFICER PANEL – {self.name}",
            font=("Consolas", 16, "bold"),
            foreground="#39ff14"
        ).pack(side="left")

        ttk.Button(
            top,
            text="Logout",
            command=self.logout
        ).pack(side="right", padx=5)

        # ---- TASK LIST ----
        self.tree = ttk.Treeview(
            self,
            columns=(
                "id", "task", "engineer", "technician",
                "status", "progress", "updated"
            ),
            show="headings"
        )

        headings = [
            "ID", "TASK", "ENGINEER",
            "TECHNICIAN", "STATUS", "PROGRESS %", "UPDATED"
        ]

        for col, head in zip(self.tree["columns"], headings):
            self.tree.heading(col, text=head, anchor="center")
            self.tree.column(col, width=140, anchor="center")

        self.tree.column("task", width=360)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- ACTION BUTTONS ----
        btns = ttk.Frame(self)
        btns.pack(pady=8)

        ttk.Button(
            btns,
            text="Assign Technician",
            command=self.assign_popup
        ).pack(side="left", padx=5)

        ttk.Button(
            btns,
            text="Set Running",
            command=lambda: self.update_status("Running")
        ).pack(side="left", padx=5)

        ttk.Button(
            btns,
            text="Set Completed",
            command=lambda: self.update_status("Completed")
        ).pack(side="left", padx=5)

        self.load()

    # ---------------- LOAD TASKS ----------------
    def load(self):
        self.tree.delete(*self.tree.get_children())

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, engineer,
                   IFNULL(technician,'-'),
                   status,
                   IFNULL(progress,0),
                   updated_at
            FROM tasks
            WHERE officer=?
        """, (self.name,))

        for r in cur.fetchall():
            self.tree.insert("", "end", values=r)

        conn.close()

    # ---------------- AUTO REFRESH ----------------
    def auto_refresh(self):
        try:
            self.load()
        except:
            return
        self.after(3000, self.auto_refresh)   # 🔁 every 3 sec

    # ---------------- UPDATE STATUS ----------------
    def update_status(self, status):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a task")
            return

        tid = self.tree.item(sel[0])["values"][0]
        now = datetime.now().strftime('%d-%b-%Y %I:%M %p')

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET status=?, updated_at=? WHERE id=?",
            (status, now, tid)
        )
        conn.commit()
        conn.close()
        self.load()

    # ---------------- ASSIGN TECHNICIAN ----------------
    def assign_popup(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a task")
            return

        tid = self.tree.item(sel[0])["values"][0]

        win = tk.Toplevel(self)
        win.title("Assign Technician")
        win.geometry("300x200")
        apply_hacker_theme(win)

        ttk.Label(
            win,
            text="Select Technician",
            font=("Consolas", 12, "bold"),
            foreground="#39ff14"
        ).pack(pady=10)

        tech = ttk.Combobox(win, state="readonly", width=26)
        tech.pack(pady=10)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE role='technician'")
        tech["values"] = [r[0] for r in cur.fetchall()]
        conn.close()

        def assign():
            if not tech.get():
                return
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE tasks SET technician=? WHERE id=?",
                (tech.get(), tid)
            )
            conn.commit()
            conn.close()
            win.destroy()
            self.load()

        ttk.Button(win, text="ASSIGN", command=assign).pack(pady=15)

    # ---------------- LOGOUT ----------------
    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.root.destroy()
            self.login_win.deiconify()



# ================= ADMIN PANEL =================

class AdminPanel(ttk.Frame):
    def __init__(self,parent,root,login_win):
        super().__init__(parent)
        self.root=root
        self.login_win=login_win
        self.pack(fill="both",expand=True)
        self.ui()

    def ui(self):
        top=ttk.Frame(self); top.pack(fill="x",padx=10)
        ttk.Label(
            top,
            text="ADMIN DASHBOARD",
            font=("Consolas",15,"bold"),
            foreground="#39ff14"
        ).pack(side="left")

        b=ttk.Button(
            top,
            text="LOGOUT",
            command=lambda:logout(self.root,self.login_win)
        )
        b.pack(side="right")
        glow(b)

        nb=ttk.Notebook(self)
        nb.pack(fill="both",expand=True)

        self.users_frame=ttk.Frame(nb)
        self.tasks_frame=ttk.Frame(nb)
        self.report_frame=ttk.Frame(nb)

        nb.add(self.users_frame,text="👤 USERS")
        nb.add(self.tasks_frame,text="📝 TASKS")
        nb.add(self.report_frame,text="📊 REPORT")

        self.users_tab()
        self.tasks_tab()
        self.report_tab()

    # ---------- USERS TAB ----------
    def users_tab(self):
        f=self.users_frame

        top=ttk.LabelFrame(f,text="Create User",padding=10)
        top.pack(fill="x",padx=10,pady=5)

        name=ttk.Entry(top,width=18)
        username=ttk.Entry(top,width=14)
        password=ttk.Entry(top,width=14,show="*")

        # ✅ Technician role added here
        role=ttk.Combobox(
            top,
            values=["admin","engineer","officer","technician"],
            state="readonly",
            width=14
        )

        fields=[
            ("Name",name),
            ("Username",username),
            ("Password",password),
            ("Role",role)
        ]

        for i,(l,w) in enumerate(fields):
            ttk.Label(top,text=l).grid(row=0,column=i*2)
            w.grid(row=0,column=i*2+1,padx=4)

        def create_user():
            if not all([name.get(),username.get(),password.get(),role.get()]):
                messagebox.showwarning("Missing","Fill all fields")
                return

            conn=get_db();cur=conn.cursor()
            cur.execute(
                "INSERT INTO users VALUES (?,?,?,?)",
                (
                    username.get(),
                    hash_password(password.get()),
                    role.get(),
                    name.get()
                )
            )
            conn.commit();conn.close()
            self.load_users()

        b=ttk.Button(top,text="CREATE",command=create_user)
        b.grid(row=0,column=8,padx=10)
        glow(b)

        self.tv=ttk.Treeview(
            f,
            columns=("name","username","role"),
            show="headings"
        )

        for c in self.tv["columns"]:
            self.tv.heading(c,text=c.upper(),anchor="center")
            self.tv.column(c,width=200,anchor="center")

        self.tv.pack(fill="both",expand=True,padx=10,pady=10)

        d=ttk.Button(
            f,
            text="DELETE SELECTED USER",
            command=self.delete_user
        )
        d.pack(pady=5)
        glow(d)

        self.load_users()

    def load_users(self):
        self.tv.delete(*self.tv.get_children())
        conn=get_db();cur=conn.cursor()
        cur.execute("SELECT name,username,role FROM users")
        for r in cur.fetchall():
            self.tv.insert("", "end", values=r)
        conn.close()

    def delete_user(self):
        sel=self.tv.selection()
        if not sel: return
        uname=self.tv.item(sel[0])["values"][1]
        if uname=="admin": return

        conn=get_db();cur=conn.cursor()
        cur.execute("DELETE FROM users WHERE username=?", (uname,))
        conn.commit();conn.close()
        self.load_users()

    # ---------- TASKS TAB ----------
    def tasks_tab(self):
        tv=ttk.Treeview(
            self.tasks_frame,
            columns=("id","title","model","urgency","engineer","officer","status","time"),
            show="headings"
        )

        for c in tv["columns"]:
            tv.heading(c,text=c.upper(),anchor="center")
            tv.column(c,width=120,anchor="center")

        tv.pack(fill="both",expand=True,padx=10,pady=10)

        conn=get_db();cur=conn.cursor()
        cur.execute("""
            SELECT id,title,model,urgency,engineer,officer,status,updated_at
            FROM tasks
        """)
        for r in cur.fetchall():
            tv.insert("", "end", values=r)
        conn.close()

    # ---------- REPORT TAB ----------
    def report_tab(self):
        tv=ttk.Treeview(
            self.report_frame,
            columns=("engineer","pending","running","completed"),
            show="headings"
        )

        for c in tv["columns"]:
            tv.heading(c,text=c.upper(),anchor="center")
            tv.column(c,width=180,anchor="center")

        tv.pack(fill="both",expand=True,padx=10,pady=10)

        conn=get_db();cur=conn.cursor()
        cur.execute("""
            SELECT engineer,
            SUM(status='Pending'),
            SUM(status='Running'),
            SUM(status='Completed')
            FROM tasks
            GROUP BY engineer
        """)
        for r in cur.fetchall():
            tv.insert("", "end", values=r)
        conn.close()


# ================= LOGIN =================

class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("360x260")
        apply_hacker_theme(self)

        f=ttk.Frame(self,padding=20); f.pack(fill="both",expand=True)
        ttk.Label(f,text="DAILY WORK UPDATE",
                  font=("Consolas",14,"bold"),
                  foreground="#39ff14").pack(pady=10)

        ttk.Label(f,text="User ID").pack(anchor="w")
        self.u=ttk.Entry(f); self.u.pack(fill="x")
        ttk.Label(f,text="Password").pack(anchor="w",pady=(10,0))
        self.p=ttk.Entry(f,show="*"); self.p.pack(fill="x")

        ttk.Button(f,text="LOGIN",command=self.login).pack(pady=15)

    def login(self):
        conn=get_db();cur=conn.cursor()
        cur.execute(
            "SELECT role FROM users WHERE username=? AND password_hash=?",
            (self.u.get(), hash_password(self.p.get()))
        )
        r=cur.fetchone()
        conn.close()
        if not r:
            messagebox.showerror("Error","Invalid Login")
            return

        self.withdraw()
        self.dashboard=tk.Toplevel(self)
        self.dashboard.geometry("1200x600")
        apply_hacker_theme(self.dashboard)

        role=r[0]; user=self.u.get()

        if role=="admin":
            AdminPanel(self.dashboard,self.dashboard,self)
        elif role=="engineer":
            EngineerPanel(self.dashboard,self.dashboard,self,user)
        elif role=="officer":
            OfficerPanel(self.dashboard,self.dashboard,self,user)
        elif role=="technician":
            TechnicianPanel(self.dashboard,self.dashboard,self,user)

# ================= MAIN =================

if __name__=="__main__":
    init_db()
    Login().mainloop()

