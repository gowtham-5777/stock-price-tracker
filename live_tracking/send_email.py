import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime  # ✅ ADD THIS
import os

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

def send_email(subject, body, sender="podboost23@gmail.com", password="euvkgioyegwvkfmi", receiver="gauthamkranthi0@gmail.com"):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("✅ Email sent")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

    # ✅ LOG the alert
    try:
        with open("logs/email_alerts.log", "a") as log_file:
            log_file.write(f"[{datetime.now()}] {subject}\n{body}\n\n")
    except Exception as log_err:
        print(f"⚠️ Failed to write log: {log_err}")
