# 🔐 RBAC Security Demo

A Flask-based cybersecurity web application demonstrating **Role-Based Access Control (RBAC)** using Admin, Patient, and Doctor roles.

The project includes secure authentication, authorization checks, password hashing, access control, healthcare-style record sharing, and audit logging.

## 📌 Project Overview

Role-Based Access Control is a security model that restricts system access based on a user's assigned role.

This project demonstrates how different users receive different permissions:

### 👨‍💼 Admin
- View all users
- Change user roles
- Review security audit logs

### 👤 Patient
- Create records
- View own records
- Grant doctors access to selected records

### 🩺 Doctor
- View only records explicitly authorized by patients

The system prevents users from accessing areas outside their assigned role.

## 🚀 Features

- Secure login system
- Password hashing using Werkzeug
- Role-Based Access Control
- Admin, Patient, and Doctor roles
- Route-level authorization
- Unauthorized access detection
- Patient record creation
- Doctor access authorization
- SQLite database
- Security audit logging
- Session-based authentication
- Responsive dark-themed interface

## 🛠 Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- Werkzeug
- Jinja2
- Git
- GitHub

## 📂 Project Structure

```text
rbac-security-demo/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── admin.html
│   ├── patient.html
│   └── doctor.html
│
└── static/
    └── style.css

USER
                     │
                     ▼
                  LOGIN
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
        ADMIN      PATIENT     DOCTOR
          │          │          │
          │          │          │
          ▼          ▼          ▼
    Manage Users   Create      View Only
    Change Roles   Records     Authorized
    View Logs      Grant       Records
                   Access

👥 Demo Accounts
Role	Username	Password
Admin	admin	Admin123!
Patient	patient1	Patient123!
Doctor	doctor1	Doctor123!


These credentials are included only for demonstration purposes.

🛡 Security Features
Password Hashing
Passwords are not stored in plain text.
The application uses Werkzeug:
generate_password_hash()check_password_hash()


Role-Based Authorization
Protected routes use role checks such as:
@role_required("admin")


@role_required("patient")


@role_required("doctor")


Users who attempt to access an unauthorized area are denied access and the attempt can be recorded in the audit log.

📁 Patient Record Access
Patients can create records such as:
Medical Test Record
Sample confidential record for RBAC demonstration.

Patients can then choose which doctor is allowed to view the record.
Doctors cannot automatically access every patient's data.

📋 Security Audit Logging
The application records important security events, including:
- Successful login
- Failed login attempts
- User logout
- Record creation
- Doctor access authorization
- Authorized record viewing
- Role changes
- Unauthorized access attempts
Example:
admin      Successful login
patient1   Created record: Medical Test Record
patient1   Granted doctor access to record 1
doctor1    Viewed authorized records
doctor1    User logged out

▶️ How to Run
Install the required packages:
python -m pip install -r requirements.txt

Run the application:
python app.py

Then open:
http://127.0.0.1:5000

🗄 Database
The application uses SQLite.
The following tables are automatically created:
users
records
access_control
audit_logs

The database file is generated locally as:
rbac.db

It is excluded from GitHub using .gitignore.

🔄 Example Workflow
Patient Login
      ↓
Create Record
      ↓
Grant Access to Doctor
      ↓
Patient Logout
      ↓
Doctor Login
      ↓
View Authorized Record
      ↓
Doctor Logout
      ↓
Admin Login
      ↓
Review Audit Logs

📚 Skills Demonstrated
- Python web development
- Flask
- Authentication
- Authorization
- Role-Based Access Control
- Password hashing
- Session management
- SQLite database design
- Audit logging
- Secure route protection
- HTML/CSS development
- Git version control

🔐 Security Note
This project is intended as an educational cybersecurity demonstration.
For a production environment, additional controls should be implemented, including:
- CSRF protection
- Environment-based secret keys
- HTTPS
- Stronger session configuration
- Database access controls
- Rate limiting
- Multi-factor authentication
- More comprehensive input validation

👩‍💻 Author
Viloshini Peragasam
AI & Cybersecurity Student