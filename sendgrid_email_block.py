import smtplib
from email.message import EmailMessage

def send_email(to, score, advice):
    msg = EmailMessage()
    msg.set_content(f"Your credit score: {score}. Advice: {advice}")
    msg['Subject'] = "Your Farmer Credit Score"
    msg['From'] = "your@email.com"
    msg['To'] = to
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("your@email.com", "your_password")
        smtp.send_message(msg)
# Usage: send_email("farmer@email.com", score, advice)