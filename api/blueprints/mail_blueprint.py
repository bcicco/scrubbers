import azure.functions as func
import logging
import smtplib
from email.mime.text import MIMEText
import imaplib  # Lets Python talk to IMAP servers using the protocol
import email    # Allows the emails to be read
import json

mailBP = func.Blueprint()


@mailBP.route(route="send_mail", auth_level=func.AuthLevel.ANONYMOUS)
def send_mail(req: func.HttpRequest) -> func.HttpResponse:
    """Sends an email to a contact
    req params:
        - sending email
        - contact_email
        - email_body
        - email_subject
    outputs:
        - success / failure http response"""
    
    logging.info("Python HTTP trigger function processed a request.")
    
    sending_email = req.params.get("sender")
    contact_email = req.params.get("contact")
    email_body = req.params.get("body")
    email_subject = req.params.get("subject")

    missing = []
    if not sending_email:
        missing.append("sending_email")
    if not contact_email:
        missing.append("contact_email")
    if not email_body:
        missing.append("email_body")
    if not email_subject:
        missing.append("email_subject")

    if missing:
        return func.HttpResponse(
            json.dumps(
                {"error": "Missing required query parameters", "missing": missing}
            ),
            status_code=400,
            mimetype="application/json",
        )
    msg = MIMEText(email_body)
    msg["Subject"] = email_subject
    msg["From"] = sending_email
    msg["To"] = contact_email
    try:
        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as s:
            s.login(sending_email, "Passw0rd1")
            s.send_message(msg)
    except Exception as e:
        return func.HttpResponse(f"Internal server error, error: {e}")
    return func.HttpResponse(f"Message to {contact_email} sent successfully")

@mailBP.route(route="read_mail", auth_level=func.AuthLevel.ANONYMOUS)
def read_mail(req: func.HttpRequest) -> func.HttpResponse:
    """Reads UNREAD emails, emails opting out by replying "STOP" need to be actioned 
    to be put into a database not to contact. All other emails are forwarded on 
    to the chosen email.
    
    req params:
        - Outbound email 
        - Central email
    outputs:
        - success / failure http response
    """

    logging.info("Python HTTP trigger function processed a request.")

    outbound_email = req.params.get("outbound_email")
    central_email = req.params.get("central_email")

    missing = []
    if not outbound_email:
        missing.append("outbound_email")
    if not central_email:
        missing.append("central_email")

    if missing:
        return func.HttpResponse(
            json.dumps(
                {"error": "Missing required query parameters", "missing": missing}
            ),
            status_code=400,
            mimetype="application/json",
        )

    # Function to extract body text from an email
    def get_body(msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
        else:
            return msg.get_payload(decode=True).decode(errors="ignore")

    # Connect to IMAP Server and log in
    mail = imaplib.IMAP4_SSL("mail.privateemail.com")
    mail.login(outbound_email, "Passw0rd1")
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
            print("Found STOP — add to Global Do Not Mail list")
            # TODO: Add code to handle STOP
        else:
            print("Forwarding email to personal inbox...")

            # Build a simple forwarded message
            fwd_msg = MIMEText(body)
            fwd_msg["Subject"] = "FWD: " + (msg["Subject"] or "")
            fwd_msg["From"] = outbound_email
            fwd_msg["To"] = central_email   # 👈 replace with your real personal address

            # Send it via Gmail SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(outbound_email, "Passw0rd1")
                smtp.send_message(fwd_msg)
