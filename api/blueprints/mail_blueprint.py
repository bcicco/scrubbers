import azure.functions as func
import logging
import smtplib
from email.mime.text import MIMEText
import json

mailBP = func.Blueprint()


@mailBP.route(route="send_mail", auth_level=func.AuthLevel.ANONYMOUS)
def send_mail(req: func.HttpRequest) -> func.HttpResponse:
    """Sends an email to a contact
    req params:
        - contact_email
        - email_body
        - email_subject
    outputs:
        - success / failure http response"""
    
    logging.info("Python HTTP trigger function processed a request.")

    contact_email = req.params.get("contact")
    email_body = req.params.get("body")
    email_subject = req.params.get("subject")

    missing = []
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
    msg["From"] = "percy@randallsstore.com.au"
    msg["To"] = contact_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login("percy@randallsstore.com.au", "tfaf libd uqws rtwv")
            s.send_message(msg)
    except Exception as e:
        return func.HttpResponse(f"Internal server error, error: {e}")
    return func.HttpResponse(f"Message to {contact_email} sent successfully")
