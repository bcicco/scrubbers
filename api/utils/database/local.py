from ..businesses import Businesses
import pyodbc
from typing import List
from datetime import datetime


def insert_leads(
    businesses: Businesses, target_area, server_creds: List[str], product_id, customer_id
):

    conn = pyodbc.connect(
        f"DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

    cursor = conn.cursor()

    try:

        current_date = datetime.now().date()

        for biz in businesses.business_leads:
            try:

                print(f"Processing business: {biz.name}")

                # Step 1: Insert or update in Business_Registrar table
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM Business_Registrar WHERE Contact_Email = ?)
                    BEGIN
                        INSERT INTO Business_Registrar (Contact_Email, Business_Name, Opted_Out, Currently_Contacting, Status)
                        VALUES (?, ?, 0, 0, 'New')
                    END
                """, (
                    biz.contact_email,  # Check if exists
                    biz.contact_email,  # Insert email
                    biz.name           # Insert business name
                ))
                print(f"Processing business: {biz.name}")
                cursor.execute(
                    """
                    INSERT INTO Leads 
                    (Customer_ID, Product_Id, Contact_Email, Business_Name, Business_Description, Personalised_Statement, Review, Date_Found, Status, Last_Contact_Date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        customer_id,
                        product_id,
                        biz.contact_email,
                        biz.name,
                        getattr(biz, "description", None),
                        biz.personalised_statement,
                        biz.review,
                        current_date, 
                        "New",  # Status
                        None,  # Last_Contact_Date (NULL for new leads)
                    ),
                )

                print(f"Successfully inserted lead for {biz.name}")

            except Exception as biz_error:
                error_safe = str(biz_error).encode("ascii", "ignore").decode("ascii")
                print(f"Error processing business {biz.name}: {error_safe}")
                # Continue with other businesses instead of failing completely
                continue

        conn.commit()
        print(
            f"Successfully pushed {len(businesses.business_leads)} businesses to database"
        )

    except Exception as e:
        conn.rollback()
        error_safe = str(e).encode("ascii", "ignore").decode("ascii")
        print(f"Database error: {error_safe}")
        raise Exception(error_safe)
    finally:
        cursor.close()
        conn.close()

def complete_lead(server_creds, email):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    cursor.execute(f"""
    UPDATE Leads
    SET Status = 'complete'
    WHERE Contact_Email = '{email}' 
    AND (Status <> 'complete' OR Status IS NULL)
""")
    
    conn.commit()

    
    cursor.close()
    conn.close()

def unfinished_lead_exists(server_creds, email: str) -> bool:
    conn = pyodbc.connect(
        f"DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1
        FROM Leads
        WHERE Contact_Email = 'bcicco.solutions@outlook.com' 
        AND (Status <> 'complete' OR Status IS NULL)
    """)
    result = cursor.fetchone()
    cursor.close()
    return result is not None

def email_exists(server_creds, email: str) -> bool:
    conn = pyodbc.connect(
        f"DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1
        FROM Business_Registrar
        WHERE Contact_Email = '{email}';
    """)
    result = cursor.fetchone()
    cursor.close()
    return result is not None


if __name__ == '__main__':
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
            if(email_exists(server_creds, msg["From"])):
                if(unfinished_lead_exists):
                    complete_lead(server_creds, msg["From"])

        else:
            if(email_exists(server_creds, msg["From"])):
                if(unfinished_lead_exists):
                    complete_lead(server_creds, msg["From"])
                with smtplib.SMTP_SSL(SMTP_SERVER, 465) as smtp:
                    fwd_msg = MIMEText(body)
                    fwd_msg["subject"] = msg["From"]
                    fwd_msg["From"] = EMAIL_ACCOUNT
                    fwd_msg["To"] = "percy@randallsstore.com.au"
                    smtp.login(EMAIL_ACCOUNT, PASSWORD)
                    smtp.send_message(fwd_msg)
        mail.store(num, '+FLAGS', '\\Seen')
def opt_out_business(server_creds, email):
    conn = pyodbc.connect(
        f"DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    cursor = conn.cursor()
    cursor.execute(
    """
    UPDATE Business_Registrar
    SET Opted_Out = 1
    WHERE Contact_Email = '{email}'
    """)
    conn.commit()
    cursor.close()
    conn.close()
