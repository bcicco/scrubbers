# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(readmailBP) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints

import azure.functions as func
import logging
import smtplib
from email.mime.text import MIMEText
import imaplib  # Lets Python talk to IMAP servers using the protocol
import email    # Allows the emails to be read
import json

IMAP_SERVER = "mail.privateemail.com"  # Connect to Gmail's IMAP server
EMAIL_ACCOUNT = "percy@randallstore.com.au"
PASSWORD = "Passw0rd1"  

readmailBP = func.Blueprint()
def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")

@readmailBP.timer_trigger(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def read_new_mail(myTimer: func.TimerRequest) -> None:
    # Gmail IMAP server details


    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)

    mail.select("inbox")

    # Search for unread emails
    status, data = mail.search(None, "UNSEEN")
    mail_ids = data[0].split()

    # Loop through unread emails
    for num in mail_ids:
        status, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract the body
        body = get_body(msg)

        print("From:", msg["From"])
        print("Subject:", msg["Subject"])
        print("Body:", body)

        # Check for STOP keyword
        if body.upper() == "STOP":
            print("Found STOP — add to Global Do Not Mail list")
            fwd_msg = MIMEText(body)
            fwd_msg["Subject"] = "STOP FOUND GOOD SIR (NOT A MINORITY)" 
            fwd_msg["From"] = EMAIL_ACCOUNT
            fwd_msg["To"] = "perceval.randall@randallstore.com.au"  
            # Send it via Gmail SMTP
            with smtplib.SMTP_SSL("mail.privateemail.com", 465) as smtp:
                smtp.login(EMAIL_ACCOUNT, PASSWORD)
                smtp.send_message(fwd_msg)

        else:
            print("Forwarding email to personal inbox...")

            # Build a simple forwarded message
            fwd_msg = MIMEText(body)
            fwd_msg["Subject"] = "FWD: " + (msg["Subject"] or "")
            fwd_msg["From"] = EMAIL_ACCOUNT
            fwd_msg["To"] = "percevalrandall@gmail.com"  
            # Send it via Gmail SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ACCOUNT, PASSWORD)
                smtp.send_message(fwd_msg)
        mail.store(num, '+FLAGS', '\\Seen')
