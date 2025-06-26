import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime


conn = sqlite3.connect('todo_advanced.db')
c = conn.cursor()


c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    due_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')
conn.commit()


class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do List")
        self.theme = "light"
        self.user_id = None
        self.setup_login_ui()

    def setup_login_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Username").grid(row=0, column=0)
        tk.Label(self.root, text="Password").grid(row=1, column=0)
        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")
        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        tk.Button(self.root, text="Login", command=self.login).grid(row=2, column=0)
        tk.Button(self.root, text="Sign Up", command=self.signup).grid(row=2, column=1)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
        if result:
            self.user_id = result[0]
            self.setup_main_ui()
        else:
            messagebox.showerror("Error", "Invalid login")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created. You can log in now.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    def setup_main_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("500x500")
        self.task_entry = tk.Entry(self.root, width=30)
        self.task_entry.grid(row=0, column=0, padx=10, pady=10)
        self.date_entry = tk.Entry(self.root, width=20)
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.grid(row=0, column=1)

        tk.Button(self.root, text="Add Task", command=self.add_task).grid(row=0, column=2)
        tk.Button(self.root, text="Delete Task", command=self.delete_task).grid(row=1, column=2)
        tk.Button(self.root, text="Toggle Theme", command=self.toggle_theme).grid(row=1, column=1)

        self.tree = ttk.Treeview(self.root, columns=("Task", "Due"), show="headings")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Due", text="Due Date")
        self.tree.grid(row=2, column=0, columnspan=3, pady=20)
        self.refresh_tasks()
        self.apply_theme()

    def refresh_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        c.execute("SELECT id, task, due_date FROM tasks WHERE user_id=?", (self.user_id,))
        for task in c.fetchall():
            self.tree.insert('', 'end', iid=task[0], values=(task[1], task[2]))

    def add_task(self):
        task = self.task_entry.get().strip()
        due_date = self.date_entry.get().strip()
        if not task or not due_date:
            messagebox.showwarning("Warning", "Please fill both fields")
            return
        try:
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid date format")
            return
        c.execute("INSERT INTO tasks (user_id, task, due_date) VALUES (?, ?, ?)",
                  (self.user_id, task, due_date))
        conn.commit()
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.refresh_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if selected:
            task_id = selected[0]
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()
            self.refresh_tasks()
        else:
            messagebox.showinfo("Info", "Select a task to delete.")

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        bg = "#2c2c2c" if self.theme == "dark" else "#ffffff"
        fg = "#ffffff" if self.theme == "dark" else "#000000"
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            widget.configure(bg=bg, fg=fg)
        self.tree.tag_configure('evenrow', background=bg, foreground=fg)


root = tk.Tk()
app = ToDoApp(root)
root.mainloop()

