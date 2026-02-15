from flask import Flask, render_template, request, redirect, url_for, session
import datetime
app = Flask(__name__)
app.secret_key = 'super_secret_key_cee_12345'
employees_data = [{"id": "RD6723849001", "password": "ABCDE12345", "name": "Rangsan Somkane", "role": "Head of Department", "dept": "Management", "status": "Active", "avatar": "https://ui-avatars.com/api/?name=Rangsan+Somkane&background=0D8ABC&color=fff"}]
projects_data = [{"id": 1, "title": "AI System", "assignee": "Rangsan Somkane", "status": "In Progress", "due": "2026-03-01"}]
announcements_data = [{"id": 1, "title": "Welcome", "content": "Welcome to System", "date": "15 Feb 2026"}]
def get_stats():
    return {"total_emp": len(employees_data), "total_projects": len(projects_data), "active_projects": 1}
@app.context_processor
def inject_global_data():
    return dict(stats=get_stats())
@app.route('/')
def home(): return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        user = next((e for e in employees_data if e['id'] == u), None)
        if user and user['password'] == p:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['avatar'] = user['avatar']
            return redirect(url_for('dashboard'))
        error = "Invalid Credentials"
    return render_template('login.html', error=error)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', announcements=announcements_data, active_page='dashboard')
@app.route('/hr')
def hr():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('hr.html', employees=employees_data, active_page='hr')
@app.route('/tasks')
def tasks():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('tasks.html', projects=projects_data, employees=employees_data, active_page='tasks')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
