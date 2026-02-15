from flask import Flask, render_template, request, redirect, url_for, session
import datetime
app = Flask(__name__)
app.secret_key = 'super_secret_key_for_cee_project' 
employees_data = [
    {
        "id": "RD6723849001", 
        "password": "ABCDE12345", 
        "name": "Rangsan Somkane", 
        "role": "Head of Department", 
        "dept": "Management", 
        "status": "Active", 
        "is_first_login": False,
        "avatar": "https://ui-avatars.com/api/?name=Rangsan+Somkane&background=0D8ABC&color=fff"
    }
]
projects_data = [
    {"id": 1, "title": "AI Core System Update", "assignee": "Rangsan Somkane", "status": "In Progress", "due": "2026-03-01"},
    {"id": 2, "title": "Database Migration", "assignee": "Unassigned", "status": "Pending", "due": "2026-03-10"}
]
announcements_data = [
    {"id": 1, "title": "Welcome to New Era", "content": "ขอต้อนรับสู่ระบบบริหารงานใหม่ ขอให้ทุกคนตั้งใจทำงาน", "date": "15 Feb 2026"}
]
activities_data = [
    {"time": "Now", "text": "System initialized and ready.", "type": "system"}
]
def get_current_user():
    """ดึงข้อมูลผู้ใช้ปัจจุบันจาก Session"""
    if 'user_id' not in session: return None
    return next((emp for emp in employees_data if emp['id'] == session['user_id']), None)
def get_stats():
    """คำนวณตัวเลขสถิติเพื่อนำไปโชว์ในการ์ด"""
    return {
        "total_emp": len(employees_data),
        "total_projects": len(projects_data),
        "active_projects": len([p for p in projects_data if p['status'] == 'In Progress'])
    }
def log_activity(text):
    """ฟังก์ชันสำหรับบันทึก Log ความเคลื่อนไหว"""
    time_str = datetime.datetime.now().strftime("%H:%M")
    activities_data.insert(0, {"time": time_str, "text": text})
    if len(activities_data) > 10: activities_data.pop()
@app.context_processor
def inject_global_data():
    """ส่ง stats และ user ให้ทุกหน้าอัตโนมัติ ป้องกันปัญหา 'stats is undefined'"""
    user = get_current_user()
    return dict(
        stats=get_stats(),
        user=user if user else {"name": "Guest", "role": "Visitor", "avatar": "https://ui-avatars.com/api/?name=G&background=ccc"}
    )
@app.route('/')
def home():
    return redirect(url_for('login'))
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
            log_activity(f"{user['name']} เข้าสู่ระบบ")
            if user.get('is_first_login'): return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            error = "รหัสผ่านหรือไอดีไม่ถูกต้อง"
    return render_template('login.html', error=error)
@app.route('/dashboard')
def dashboard():
    if not get_current_user(): return redirect(url_for('login'))
    return render_template('dashboard.html', active_page='dashboard', announcements=announcements_data, activities=activities_data)
@app.route('/tasks')
def tasks():
    if not get_current_user(): return redirect(url_for('login'))
    return render_template('tasks.html', active_page='tasks', projects=projects_data, employees=employees_data)
@app.route('/hr')
def hr():
    if not get_current_user(): return redirect(url_for('login'))
    return render_template('hr.html', active_page='hr', employees=employees_data)
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
    log_activity(f"เพิ่มพนักงานใหม่: {name}")
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
            break
    log_activity(f"แก้ไขข้อมูลพนักงาน: {request.form['name']}")
    return redirect(url_for('hr'))
@app.route('/delete_employee/<string:emp_id>')
def delete_employee(emp_id):
    if session.get('role') != 'Head of Department': return redirect(url_for('hr'))
    global employees_data
    employees_data = [e for e in employees_data if e['id'] != emp_id]
    log_activity(f"ลบพนักงานรหัส: {emp_id}")
    return redirect(url_for('hr'))
@app.route('/add_announcement', methods=['POST'])
def add_announcement():
    if session.get('role') != 'Head of Department': return redirect(url_for('dashboard'))
    new_id = len(announcements_data) + 100
    title = request.form['title']
    announcements_data.insert(0, {
        "id": new_id,
        "title": title, 
        "content": request.form['content'], 
        "date": datetime.datetime.now().strftime("%d %b %Y")
    })
    log_activity(f"โพสต์ประกาศใหม่: {title}")
    return redirect(url_for('dashboard'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True, port=5000)
