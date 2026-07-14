# Smart Attendance Management System

A web-based Smart Attendance Management System built with Flask, SQLite/MySQL, HTML, CSS, JavaScript, and Bootstrap.

## Features

- Student login
- Admin login
- Mark attendance
- Excel import/export
- Attendance percentage
- PDF reports
- Responsive Bootstrap UI

## Tech Stack

- Backend: Flask / Django
- Database: SQLite / MySQL
- Frontend: HTML, CSS, JavaScript
- UI Framework: Bootstrap
- Excel handling: pandas, openpyxl
- PDF generation: reportlab

## Project Structure

```bash
smart_attendance_system/
├── app.py
├── config.py
├── requirements.txt
├── database.db
├── uploads/
├── reports/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── student_dashboard.html
    ├── mark_attendance.html
    ├── view_attendance.html
    └── reports.html
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/smart-attendance-system.git
cd smart-attendance-system
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open in browser:
```bash
http://127.0.0.1:5000
```

## Default Admin Login

- Username: `admin`
- Password: `admin123`

## Excel Import Format

Use an Excel file with these columns:

| username | email | password | name |
|----------|-------|----------|------|
| student1 | student1@example.com | password123 | John Doe |
| student2 | student2@example.com | password123 | Jane Smith |

## Main Modules

- `app.py` — main Flask application
- `config.py` — configuration file
- `templates/` — HTML templates
- `static/` — CSS and JavaScript files
- `uploads/` — Excel files
- `reports/` — generated PDF reports

## Output Files

- Excel export for student attendance data
- PDF report for filtered attendance records

## Notes

- Attendance is stored date-wise for each student.
- Admin can import students from Excel and export attendance reports.
- Students can view their own attendance percentage and history.

## License

This project is for educational use.