from ..businesses import Businesses
import pyodbc
from typing import List
from datetime import date


def create_leads_table(server_creds: List[str]):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    cursor.execute(
    """
    CREATE TABLE counts_table (
    record_date DATE PRIMARY KEY,
    count_1 INT DEFAULT 0,
    count_2 INT DEFAULT 0,
    count_3 INT DEFAULT 0
    );
    """)

    
    conn.commit()
    print("Leads table created successfully")
    
    cursor.close()
    conn.close()


def update_leads_table(server_creds, field):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    cursor.execute(f"""
    UPDATE counts_table
    SET count_{field} = count_{field} + 1
    WHERE record_date = ?
""", date.today())
    
    conn.commit()
    print("Leads table created successfully")
    
    cursor.close()
    conn.close()