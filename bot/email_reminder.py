import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
REMINDER_EMAIL = os.getenv("REMINDER_EMAIL")

def send_reminder_email(title: str, date: str, time: str, reminder_type: str):
    try:
        if reminder_type == "1day":
            subject = f"Reminder Tomorrow — {title}"
            body = (
                f"Hi!\n\n"
                f"This is a reminder that you have an event tomorrow.\n\n"
                f"Event: {title}\n"
                f"Date: {date}\n"
                f"Time: {time}\n\n"
                f"Don't forget to prepare!\n\n"
                f"Smart Scheduler Bot"
            )
        else:
            subject = f"Starting in 1 Hour — {title}"
            body = (
                f"Hi!\n\n"
                f"Your event is starting in 1 hour.\n\n"
                f"Event: {title}\n"
                f"Date: {date}\n"
                f"Time: {time}\n\n"
                f"Get ready!\n\n"
                f"Smart Scheduler Bot"
            )

        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = REMINDER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, REMINDER_EMAIL, msg.as_string())

        print(f"Email sent: {subject}")
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False