from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'student'
    name = db.Column(db.String(100))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('User', backref='attendance_records')
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False)  # 'Present' or 'Absent'
    marked_by = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    total_students = User.query.filter_by(role='student').count()
    today = date.today()
    today_attendance = Attendance.query.filter_by(date=today).count()
    attendance_percentage = 0
    if total_students > 0:
        attendance_percentage = round((today_attendance / total_students) * 100, 2)
    
    students = User.query.filter_by(role='student').all()
    recent_attendance = Attendance.query.order_by(Attendance.date.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         today_attendance=today_attendance,
                         attendance_percentage=attendance_percentage,
                         students=students,
                         recent_attendance=recent_attendance)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    attendance_records = Attendance.query.filter_by(student_id=current_user.id).all()
    total_days = len(attendance_records)
    present_days = len([r for r in attendance_records if r.status == 'Present'])
    attendance_percentage = 0
    if total_days > 0:
        attendance_percentage = round((present_days / total_days) * 100, 2)
    
    return render_template('student_dashboard.html',
                         attendance_records=attendance_records,
                         total_days=total_days,
                         present_days=present_days,
                         attendance_percentage=attendance_percentage)

@app.route('/mark-attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        selected_date = request.form.get('date', date.today())
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        students = User.query.filter_by(role='student').all()
        
        for student in students:
            status = request.form.get(f'student_{student.id}', 'Absent')
            existing = Attendance.query.filter_by(
                student_id=student.id, 
                date=selected_date
            ).first()
            
            if existing:
                existing.status = status
            else:
                new_attendance = Attendance(
                    student_id=student.id,
                    date=selected_date,
                    status=status,
                    marked_by=current_user.id
                )
                db.session.add(new_attendance)
        
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    students = User.query.filter_by(role='student').all()
    selected_date = request.args.get('date', date.today())
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    
    return render_template('mark_attendance.html', students=students, selected_date=selected_date)

@app.route('/view-attendance', methods=['GET', 'POST'])
@login_required
def view_attendance():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    start_date = request.form.get('start_date', date.today().replace(day=1))
    end_date = request.form.get('end_date', date.today())
    student_id = request.form.get('student_id')
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    query = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    )
    
    if student_id:
        query = query.filter_by(student_id=int(student_id))
    
    attendance_records = query.order_by(Attendance.date.desc()).all()
    students = User.query.filter_by(role='student').all()
    
    return render_template('view_attendance.html',
                         attendance_records=attendance_records,
                         students=students,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/import-excel', methods=['POST'])
@login_required
def import_excel():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        df = pd.read_excel(file)
        for index, row in df.iterrows():
            username = str(row.get('username', ''))
            email = str(row.get('email', ''))
            password = str(row.get('password', 'password123'))
            name = str(row.get('name', ''))
            
            if not User.query.filter_by(username=username).first():
                new_user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    role='student',
                    name=name
                )
                db.session.add(new_user)
        
        db.session.commit()
        flash('Students imported successfully!', 'success')
    except Exception as e:
        flash(f'Error importing file: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/export-excel')
@login_required
def export_excel():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    students = User.query.filter_by(role='student').all()
    data = []
    
    for student in students:
        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
        total_days = len(attendance_records)
        present_days = len([r for r in attendance_records if r.status == 'Present'])
        percentage = round((present_days / total_days * 100), 2) if total_days > 0 else 0
        
        data.append({
            'ID': student.id,
            'Name': student.name,
            'Username': student.username,
            'Email': student.email,
            'Total Days': total_days,
            'Present Days': present_days,
            'Attendance %': percentage
        })
    
    df = pd.DataFrame(data)
    filename = 'uploads/students_export.xlsx'
    df.to_excel(filename, index=False)
    
    return send_file(filename, as_attachment=True)

@app.route('/generate-report', methods=['POST'])
@login_required
def generate_report():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    student_id = request.form.get('student_id')
    start_date = request.form.get('start_date', date.today().replace(day=1))
    end_date = request.form.get('end_date', date.today())
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    query = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    )
    
    if student_id:
        query = query.filter_by(student_id=int(student_id))
        student = User.query.get(int(student_id))
        student_name = student.name if student else 'All Students'
    else:
        student_name = 'All Students'
    
    attendance_records = query.order_by(Attendance.date.desc()).all()
    
    # Generate PDF
    filename = f'reports/attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    elements = []
    elements.append(Paragraph(f'Attendance Report - {student_name}', styles['Heading1']))
    elements.append(Paragraph(f'Period: {start_date} to {end_date}', styles['Normal']))
    elements.append(Paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
    elements.append(Paragraph('<br/>', styles['Normal']))
    
    data = [['Date', 'Student', 'Status']]
    for record in attendance_records:
        student = User.query.get(record.student_id)
        data.append([
            str(record.date),
            student.name if student else 'Unknown',
            record.status
        ])
    
    table = Table(data, colWidths=[100, 200, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return send_file(filename, as_attachment=True)

def create_admin_user():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                email='admin@school.com',
                password=generate_password_hash('admin123'),
                role='admin',
                name='Administrator'
            )
            db.session.add(admin_user)
            db.session.commit()
            print('Admin user created: username=admin, password=admin123')

if __name__ == '__main__':
    create_admin_user()
    app.run(debug=True)