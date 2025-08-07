import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import SMTP_CONFIG

def send_email(to_email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['EMAIL']
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_CONFIG['EMAIL'], SMTP_CONFIG['PASSWORD'])
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")
