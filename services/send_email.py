import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(subject: str, body_text: str, receiver_email: str, attachment_path: str = None):
    """
    Sends an email with a subject, body, and optional attachment.
    Configuration is loaded from a .env file.
    """
    # --------------------- Configuration ---------------------
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, receiver_email]):
        print("❌ Missing one or more required email configuration variables in .env file.")
        return

    # --------------------- Construct Email ---------------------
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add body
    msg.attach(MIMEText(body_text, "plain"))

    # Attach file if exists
    if attachment_path and Path(attachment_path).exists():
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=Path(attachment_path).name)
            part['Content-Disposition'] = f'attachment; filename="{Path(attachment_path).name}"'
            msg.attach(part)

    # --------------------- Send Email ---------------------
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == '__main__':
    # This block is for testing the email function directly
    print("Running test email...")
    test_subject = "Test: Research Paper Summary"
    test_body = """
Hello,

This is a test email. If you received this, the send_email function is working.
Attached is a sample research paper.

Best regards,
Your Research Assistant
"""
    # This requires a .env file with RECEIVER_EMAIL set
    test_receiver = os.getenv("RECEIVER_EMAIL")
    # Make sure this test file exists or change the path
    test_attachment = Path(r"D:\Project\research-paper-summarizer\services\data\PolySkill Learning Generalizable Skills Through Polymorphic Abstraction.pdf")

    if test_receiver:
        if test_attachment.exists():
            send_email(test_subject, test_body, test_receiver, str(test_attachment))
        else:
            print(f"⚠️ Test attachment not found at: {test_attachment}")
            # Optionally send without attachment
            send_email(test_subject, test_body, test_receiver)
    else:
        print("❌ Cannot run test: RECEIVER_EMAIL is not set in the .env file.")