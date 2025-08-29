from ..businesses import Businesses
import pyodbc
from typing import List
from datetime import datetime


def insert_leads(
    businesses: Businesses, target_area, server_creds: List[str], product_id
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
                    (Product_Id, Contact_Email, Business_Name, Business_Description, Personalised_Statement, Date_Found, Status, Last_Contact_Date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        product_id,
                        biz.contact_email,
                        biz.name,
                        getattr(biz, "description", None),
                        f"Lead for {getattr(biz, 'industry', 'Unknown')} business in {target_area}",  # Personalised_Statement placeholder, will update in future.
                        current_date,  # Date_Found
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
