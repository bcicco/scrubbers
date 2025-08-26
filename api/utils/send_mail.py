import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Hello from my domain via Gmail SMTP!")
msg["Subject"] = "Test"
msg["From"] = "percy@randallsstore.com.au"
msg["To"] = "perceval.randall@my.jcu.edu.au"

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login("percy@randallsstore.com.au", "tfaf libd uqws rtwv")
    s.send_message(msg)
