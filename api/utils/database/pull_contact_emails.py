from typing import List
import pyodbc
def get_email_addresses(server_creds: List[str], customer_id):
    conn = pyodbc.connect(
    f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    cursor = conn.cursor()

    # get emails
    cursor.execute("""
        SELECT contactEmail 
        FROM [dbo].[BusinessLeads]
        WHERE customerID = ?;
    """, (customer_id,))

    rows = cursor.fetchall()
    emails = [row[0] for row in rows]
    cursor.close()
    conn.close()
    return emails
