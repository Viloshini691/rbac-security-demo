from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from werkzeug.security import check_password_hash

from database import (
    get_db,
    initialize_database,
    log_action,
)


app = Flask(__name__)
app.secret_key = "portfolio-rbac-demo-secret"


# -----------------------
# Authentication Helpers
# -----------------------

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


def role_required(required_role):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("login"))

            if session.get("role") != required_role:
                log_action(
                    session.get("username", "Unknown"),
                    f"Unauthorized access attempt to {required_role} area",
                )

                flash(
                    "Access denied. You do not have permission.",
                    "danger",
                )

                return redirect(url_for("dashboard"))

            return view(*args, **kwargs)

        return wrapped_view

    return decorator


# -----------------------
# Login / Logout
# -----------------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password,
        ):

            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            log_action(
                username,
                "Successful login",
            )

            return redirect(url_for("dashboard"))

        log_action(
            username,
            "Failed login attempt",
        )

        flash(
            "Invalid username or password.",
            "danger",
        )

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    username = session.get("username")

    log_action(
        username,
        "User logged out",
    )

    session.clear()

    return redirect(url_for("login"))


# -----------------------
# Main Dashboard
# -----------------------

@app.route("/dashboard")
@login_required
def dashboard():

    role = session.get("role")

    if role == "admin":
        return redirect(url_for("admin_dashboard"))

    if role == "patient":
        return redirect(url_for("patient_dashboard"))

    if role == "doctor":
        return redirect(url_for("doctor_dashboard"))

    return "Unknown role", 403


# -----------------------
# Admin
# -----------------------

@app.route("/admin")
@role_required("admin")
def admin_dashboard():

    conn = get_db()

    users = conn.execute(
        """
        SELECT id, username, role
        FROM users
        ORDER BY id
        """
    ).fetchall()

    logs = conn.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY id DESC
        LIMIT 50
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        logs=logs,
    )


@app.route(
    "/admin/change-role/<int:user_id>",
    methods=["POST"],
)
@role_required("admin")
def change_role(user_id):

    new_role = request.form["role"]

    allowed_roles = [
        "admin",
        "doctor",
        "patient",
    ]

    if new_role not in allowed_roles:
        flash("Invalid role.", "danger")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()

    user = conn.execute(
        "SELECT username FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

    if user:

        conn.execute(
            """
            UPDATE users
            SET role = ?
            WHERE id = ?
            """,
            (new_role, user_id),
        )

        conn.commit()

        log_action(
            session["username"],
            f"Changed {user['username']} role to {new_role}",
        )

    conn.close()

    return redirect(url_for("admin_dashboard"))


# -----------------------
# Patient
# -----------------------

@app.route("/patient")
@role_required("patient")
def patient_dashboard():

    conn = get_db()

    records = conn.execute(
        """
        SELECT *
        FROM records
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],),
    ).fetchall()

    doctors = conn.execute(
        """
        SELECT id, username
        FROM users
        WHERE role = 'doctor'
        """
    ).fetchall()

    conn.close()

    return render_template(
        "patient.html",
        records=records,
        doctors=doctors,
    )


@app.route(
    "/patient/create-record",
    methods=["POST"],
)
@role_required("patient")
def create_record():

    title = request.form["title"]
    content = request.form["content"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO records
        (patient_id, title, content)
        VALUES (?, ?, ?)
        """,
        (
            session["user_id"],
            title,
            content,
        ),
    )

    conn.commit()
    conn.close()

    log_action(
        session["username"],
        f"Created record: {title}",
    )

    flash(
        "Record created successfully.",
        "success",
    )

    return redirect(url_for("patient_dashboard"))


@app.route(
    "/patient/grant-access",
    methods=["POST"],
)
@role_required("patient")
def grant_access():

    record_id = request.form["record_id"]
    doctor_id = request.form["doctor_id"]

    conn = get_db()

    record = conn.execute(
        """
        SELECT *
        FROM records
        WHERE id = ?
        AND patient_id = ?
        """,
        (
            record_id,
            session["user_id"],
        ),
    ).fetchone()

    if not record:
        conn.close()

        flash(
            "You cannot grant access to this record.",
            "danger",
        )

        return redirect(url_for("patient_dashboard"))

    try:
        conn.execute(
            """
            INSERT INTO access_control
            (record_id, doctor_id)
            VALUES (?, ?)
            """,
            (
                record_id,
                doctor_id,
            ),
        )

        conn.commit()

        flash(
            "Access granted successfully.",
            "success",
        )

        log_action(
            session["username"],
            f"Granted doctor access to record {record_id}",
        )

    except Exception:

        flash(
            "Doctor already has access.",
            "warning",
        )

    finally:
        conn.close()

    return redirect(url_for("patient_dashboard"))


# -----------------------
# Doctor
# -----------------------

@app.route("/doctor")
@role_required("doctor")
def doctor_dashboard():

    conn = get_db()

    records = conn.execute(
        """
        SELECT
            records.id,
            records.title,
            records.content,
            users.username AS patient_name
        FROM access_control

        JOIN records
            ON access_control.record_id = records.id

        JOIN users
            ON records.patient_id = users.id

        WHERE access_control.doctor_id = ?
        """,
        (session["user_id"],),
    ).fetchall()

    conn.close()

    log_action(
        session["username"],
        "Viewed authorized records",
    )

    return render_template(
        "doctor.html",
        records=records,
    )


if __name__ == "__main__":

    initialize_database()

    app.run(debug=True)