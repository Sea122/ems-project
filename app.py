from flask import Flask, render_template, request, redirect, url_for, session
import datetime
app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sea'
employees_data = [
    {"id": "RD6723849001", "password": "Sea+Sea=Sea12345", "name": "Rangsan Somkane", "role": "Head of Department", "dept": "Management", "status": "Active", "is_first_login": False, "avatar": "https://ui-avatars.com/api/?name=Rangsan+Somkane&background=0D8ABC&color=fff"}
]
projects_data = [
    {"id": 1, "title": "AI Core System Update", "assignee": "Rangsan Somkane", "status": "In Progress", "due": "2026-03-01"},
    {"id": 2, "title": "Database Migration", "assignee": "Unassigned", "status": "Pending", "due": "2026-03-10"}
]
announcements_data = [
    {"id": 1, "title": "Welcome to New Era", "content": "ขอต้อนรับสู่ระบบบริหารงานใหม่ ขอให้ทุกคนตั้งใจทำงาน", "date": "15 Feb 2026"}
]
activities_data = [
    {"time": "Now", "text": "System initialized.", "type": "system"}
]
def is_password_strong(password):
    return len(password) >= 4
def get_current_user():
    if 'user_id' not in session: return None
    return next((emp for emp in employees_data if emp['id'] == session['user_id']), None)
def get_stats():
    return {
        "total_emp": len(employees_data),
        "total_projects": len(projects_data),
        "active_projects": len([p for p in projects_data if p['status'] == 'In Progress'])
    }
def log_activity(text):
    time_str = datetime.datetime.now().strftime("%H:%M")
    activities_data.insert(0, {"time": time_str, "text": text, "type": "info"})
    if len(activities_data) > 10:
        activities_data.pop()
@app.route('/')
def home(): return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        user = next((emp for emp in employees_data if emp['id'] == user_id), None)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            log_activity(f"{user['name']} logged in.")
            if user.get('is_first_login'): return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Credentials"
    return render_template('login.html', error=error)
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session: return redirect(url_for('login'))
    msg = None
    if request.method == 'POST':
        new_pass = request.form['new_password']
        confirm_pass = request.form['confirm_password']
        if new_pass != confirm_pass: msg = "Passwords do not match!"
        elif not is_password_strong(new_pass): msg = "Password too weak!"
        else:
            user = get_current_user()
            if user:
                user['password'] = new_pass
                user['is_first_login'] = False
                log_activity(f"{user['name']} changed password.")
                return redirect(url_for('dashboard'))
    return render_template('change_password.html', msg=msg)
@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    if user.get('is_first_login'): return redirect(url_for('change_password'))
    return render_template('dashboard.html', user=user, active_page='dashboard', stats=get_stats(), announcements=announcements_data, activities=activities_data)
@app.route('/tasks')
def tasks():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template('tasks.html', user=user, active_page='tasks', projects=projects_data, employees=employees_data, stats=get_stats())
@app.route('/hr')
def hr():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template('hr.html', user=user, active_page='hr', employees=employees_data, stats=get_stats())
@app.route('/add_employee', methods=['POST'])
def add_employee():
    if session.get('role') != 'Head of Department': return redirect(url_for('hr'))
    name = request.form['name']
    new_emp = {
        "id": request.form['id_card'], "password": request.form['temp_pass'],
        "name": name, "role": request.form['role'], "dept": request.form['dept'],
        "status": "Active", "is_first_login": True,
        "avatar": f"https://ui-avatars.com/api/?name={name}&background=random&color=fff"
    }
    employees_data.append(new_emp)
    log_activity(f"New staff added: {name}")
    return redirect(url_for('hr'))
@app.route('/edit_employee', methods=['POST'])
def edit_employee():
    if session.get('role') != 'Head of Department': return redirect(url_for('hr'))
    emp_id = request.form['emp_id']
    for emp in employees_data:
        if emp['id'] == emp_id:
            emp['name'] = request.form['name']
            emp['role'] = request.form['role']
            emp['dept'] = request.form['dept']
            emp['avatar'] = f"https://ui-avatars.com/api/?name={request.form['name']}&background=random&color=fff"
            log_activity(f"Updated info for: {request.form['name']}")
            break
    return redirect(url_for('hr'))
@app.route('/delete_employee/<string:emp_id>')
def delete_employee(emp_id):
    if session.get('role') != 'Head of Department': return redirect(url_for('hr'))
    if emp_id == "RD6723849001": return redirect(url_for('hr'))
    global employees_data
    name_to_delete = next((e['name'] for e in employees_data if e['id'] == emp_id), "Someone")
    employees_data = [emp for emp in employees_data if emp['id'] != emp_id]
    log_activity(f"Removed staff: {name_to_delete}")
    return redirect(url_for('hr'))
@app.route('/add_task', methods=['POST'])
def add_task():
    if session.get('role') != 'Head of Department': return redirect(url_for('tasks'))
    title = request.form['title']
    projects_data.append({
        "id": len(projects_data) + 100,
        "title": title, "assignee": request.form['assignee'],
        "status": "In Progress", "due": request.form['due_date']
    })
    log_activity(f"New task assigned: {title}")
    return redirect(url_for('tasks'))
@app.route('/edit_task', methods=['POST'])
def edit_task():
    if session.get('role') != 'Head of Department': return redirect(url_for('tasks'))
    task_id = int(request.form['task_id'])
    for task in projects_data:
        if task['id'] == task_id:
            task['title'] = request.form['title']
            task['assignee'] = request.form['assignee']
            task['due'] = request.form['due_date']
            task['status'] = request.form['status']
            log_activity(f"Task updated: {request.form['title']}")
            break
    return redirect(url_for('tasks'))
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if session.get('role') != 'Head of Department': return redirect(url_for('tasks'))
    global projects_data
    projects_data = [t for t in projects_data if t['id'] != task_id]
    log_activity("A task was deleted.")
    return redirect(url_for('tasks'))
@app.route('/add_announcement', methods=['POST'])
def add_announcement():
    if session.get('role') != 'Head of Department': return redirect(url_for('dashboard'))
    title = request.form['title']
    new_id = len(announcements_data) + 100
    announcements_data.insert(0, {
        "id": new_id,
        "title": title, 
        "content": request.form['content'], 
        "date": datetime.datetime.now().strftime("%d %b %Y")
    })
    log_activity(f"New announcement: {title}")
    return redirect(url_for('dashboard'))
@app.route('/edit_announcement', methods=['POST'])
def edit_announcement():
    if session.get('role') != 'Head of Department': return redirect(url_for('dashboard'))
    ann_id = int(request.form['ann_id'])
    for ann in announcements_data:
        if ann['id'] == ann_id:
            ann['title'] = request.form['title']
            ann['content'] = request.form['content']
            log_activity(f"Edited announcement: {request.form['title']}")
            break
    return redirect(url_for('dashboard'))
@app.route('/delete_announcement/<int:ann_id>')
def delete_announcement(ann_id):
    if session.get('role') != 'Head of Department': return redirect(url_for('dashboard'))
    global announcements_data
    announcements_data = [a for a in announcements_data if a['id'] != ann_id]
    log_activity("Announcement removed.")
    return redirect(url_for('dashboard'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True, port=5000)

