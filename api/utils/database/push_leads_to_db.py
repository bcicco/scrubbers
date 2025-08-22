from ..pydantic_classes.businesses import Businesses
import pyodbc
from typing import List
def push_to_db(businesses: Businesses, customer_id, target_area, server_creds: List[str]):
    print("printing first business: ")
    print(businesses.business_leads[0])
    conn = pyodbc.connect(
    f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )

    cursor = conn.cursor()


    # Push data
    for biz in businesses.business_leads:
        print("Business: ", biz)
        cursor.execute("""
            INSERT INTO BusinessLeads
            (customerID, targetArea, businessName, businessIndustry, contactEmail, location, phoneNumber, description, size, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            target_area,  # optional field
            biz.name,
            biz.industry,
            biz.contact_email,
            getattr(biz, "location", None),
            getattr(biz, "phone", None),
            getattr(biz, "description", None),
            getattr(biz, "size", None),
            getattr(biz, "website", None)
        ))
    conn.commit()