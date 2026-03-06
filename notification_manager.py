import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


class NotificationManager:

    def send_emails(self, email_list, message):
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(MY_EMAIL, GMAIL_APP_PASSWORD)
            for email in email_list:
                msg = MIMEMultipart()
                msg["Subject"] = "New Low Price Flight!"
                msg["From"] = MY_EMAIL
                msg["To"] = email
                msg.attach(MIMEText(message, "plain", "utf-8"))
                connection.sendmail(MY_EMAIL, email, msg.as_string())