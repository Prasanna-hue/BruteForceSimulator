from flask import Flask, render_template, request
import sqlite3
import time

app = Flask(__name__)

USERNAME = "Prasanna"
PASSWORD = "pras@123"

failed_attempts = 0
lockout_until = 0

# Create database
def init_db():
    conn = sqlite3.connect("login_attempts.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

# Log login attempts
def log_attempt(username, status):
    conn = sqlite3.connect("login_attempts.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO logs(username,status) VALUES (?,?)",
        (username, status)
    )

    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def login():

    global failed_attempts, lockout_until

    message = ""

    if request.method == "POST":

        # Check lockout
        if time.time() < lockout_until:

            remaining = int(lockout_until - time.time())

            return render_template(
                "login.html",
                message=f"Account Locked. Try again in {remaining} seconds.",
                success=False
            )

        username = request.form["username"]
        password = request.form["password"]

        # Successful login
        if username == USERNAME and password == PASSWORD:

            failed_attempts = 0

            log_attempt(username, "SUCCESS")

            return render_template(
                "login.html",
                success=True,
                username=username,
                message="Login Successful!"
            )

        # Failed login
        else:

            failed_attempts += 1

            log_attempt(username, "FAILED")

            # Delay protection
            time.sleep(2)

            if failed_attempts >= 5:

                lockout_until = time.time() + 180

                message = "Too many failed attempts. Account locked for 30 seconds."

            else:

                message = f"Login Failed. Attempts: {failed_attempts}/5"

    return render_template(
        "login.html",
        message=message,
        success=False
    )

if __name__ == "__main__":
    app.run(debug=True)
