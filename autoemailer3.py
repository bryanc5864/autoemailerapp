from flask import Flask, request, render_template, redirect, url_for, flash, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import io
import random
import time

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY_HERE"  # needed for flash messages & session

# In-memory user "database". For real production, use a real DB and hash passwords.
users_db = {
    # Example user structure:
    # "demo_user": {
    #     "password": "demo_pass",
    #     "sender_email": "demo@gmail.com",
    #     "sender_password": "gmail_app_pass",
    #     "history": [],
    #     "queue": []
    # }
}

def send_bulk_emails(sender_email, sender_password, recipients, message_body,
                     smtp_server="smtp.gmail.com", smtp_port=587):
    """
    Sends an email to each (name, email_address) in recipients.
    We'll prepend "Hi {name},\n\n" automatically to the message_body.
    Returns (success_list, fail_list).

    Now modified to wait for a random delay between 1 to 2 minutes (60-120 seconds)
    between sending individual emails.
    """
    if not recipients:
        return [], [("No recipients", "No recipients")]

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    success_list = []
    fail_list = []
    subject = "Bulk Email"  # static subject; feel free to make this user-editable

    total = len(recipients)
    for index, (name, email_address) in enumerate(recipients):
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email_address
        msg["Subject"] = subject

        # Prepend a greeting automatically
        personalized_body = f"Hi {name},\n\n{message_body}"
        msg.attach(MIMEText(personalized_body, "plain"))

        try:
            server.sendmail(sender_email, email_address, msg.as_string())
            success_list.append((name, email_address))
        except Exception as e:
            fail_list.append((name, email_address, str(e)))

        # If this is not the last email, wait for a random delay between 60 and 120 seconds.
        if index < total - 1:
            delay = random.uniform(60, 120)
            time.sleep(delay)

    server.quit()
    return success_list, fail_list

@app.route("/")
def home():
    """If logged in, go to main index; otherwise, go to login."""
    if "username" in session:
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new user account (in-memory)."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        sender_email = request.form.get("sender_email", "").strip()
        sender_password = request.form.get("sender_password", "").strip()

        if not all([username, password, sender_email, sender_password]):
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if username in users_db:
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for("register"))

        # Create user in the in-memory "database"
        users_db[username] = {
            "password": password,  # plain text, insecure for real usage
            "sender_email": sender_email,
            "sender_password": sender_password,
            "history": [],
            "queue": []
        }
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Existing users can log in here."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user_data = users_db.get(username)
        if user_data and user_data["password"] == password:
            # Login success
            session["username"] = username
            # Show a paper-plane animation screen before redirecting to index
            return redirect(url_for("login_success"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/login_success")
def login_success():
    """
    Shows an animation of multiple planes flying across the screen,
    then redirects to /index after a few seconds.
    """
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    return render_template("login_success.html")

@app.route("/logout")
def logout():
    """Logs out the current user."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/index", methods=["GET", "POST"])
def index():
    """Main page: add recipients (CSV/manual), see queue, send emails."""
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    username = session["username"]
    # Safety check: ensure user still exists in the dictionary
    if username not in users_db:
        flash("User not found. Please log in again.", "error")
        session.clear()
        return redirect(url_for("login"))

    user_data = users_db[username]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_csv":
            # Add recipients from CSV
            csv_file = request.files.get("csv_file")
            if csv_file and csv_file.filename.endswith(".csv"):
                stream = io.StringIO(csv_file.stream.read().decode("UTF-8"), newline=None)
                reader = csv.reader(stream)
                # next(reader, None)  # if you want to skip a header

                count = 0
                for row in reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        email = row[1].strip()
                        user_data["queue"].append((name, email))
                        count += 1
                flash(f"Successfully added {count} recipients from CSV.", "success")
            else:
                flash("No valid CSV file selected.", "error")

        elif action == "add_manual":
            # Add a single (name, email) pair
            name = request.form.get("manual_name", "").strip()
            email = request.form.get("manual_email", "").strip()
            if name and email:
                user_data["queue"].append((name, email))
                flash(f"Added '{name}' <{email}> to the queue.", "info")
            else:
                flash("Name and email cannot be empty.", "error")

        elif action == "send_emails":
            # Send to all in queue
            message_body = request.form.get("message_body", "")
            recipients = user_data["queue"]
            sender_email = user_data["sender_email"]
            sender_password = user_data["sender_password"]

            success_list, fail_list = send_bulk_emails(
                sender_email, sender_password, recipients, message_body
            )

            flash(f"Successfully sent {len(success_list)} email(s).", "success")
            if fail_list:
                flash(f"Failed to send {len(fail_list)} email(s).", "error")

            # Update user's email history with successful sends
            for name, email in success_list:
                user_data["history"].append((name, email))

            # Clear the queue after sending
            user_data["queue"] = []

        return redirect(url_for("index"))

    return render_template("index.html", queue=user_data["queue"])

@app.route("/history")
def history():
    """Display the logged-in user's email history."""
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    username = session["username"]
    if username not in users_db:
        flash("User not found. Please log in again.", "error")
        session.clear()
        return redirect(url_for("login"))

    user_data = users_db[username]
    return render_template("history.html", history=user_data["history"])

if __name__ == "__main__":
    app.run(debug=True)
