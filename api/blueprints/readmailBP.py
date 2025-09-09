
import azure.functions as func
import smtplib
from email.mime.text import MIMEText
import imaplib 
import email    
from utils.database.business_register import opt_out_business
SMTP_SERVER = "mail.privateemail.com"  
IMAP_SERVER = "mail.privateemail.com"  
SMTP_PORT = 465
EMAIL_ACCOUNT = "percy@randallstore.com.au"
PASSWORD = "Passw0rd1"  
server_creds = [
    "ODBC Driver 17 for SQL Server",
    "scrubbresdbserver.database.windows.net",
    "scrubbersdb",
    "bcicco",
    "Chinaroll1!",
]
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
        if "STOP" in body.upper():
            opt_out_business(server_creds, msg["From"])

        else:
            print("Forwarding email to personal inbox...")

            # Build a simple forwarded message
            fwd_msg = MIMEText(body)
            fwd_msg["Subject"] = "FWD: " + (msg["Subject"] or "")
            fwd_msg["From"] = EMAIL_ACCOUNT
            fwd_msg["To"] = "perceval.randall@randallstore.com.au"  
            # Send it via Gmail SMTP
            with smtplib.SMTP_SSL(SMTP_SERVER, 465) as smtp:
                smtp.login(EMAIL_ACCOUNT, PASSWORD)
                smtp.send_message(fwd_msg)
        mail.store(num, '+FLAGS', '\\Seen')
