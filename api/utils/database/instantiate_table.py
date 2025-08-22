from typing import List
import pyodbc
def create_SQL_table(server_creds: List[str]):
    conn = pyodbc.connect(
    f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )

    cursor = conn.cursor()

    # Create table
    cursor.execute("""
    CREATE TABLE BusinessLeads (
        leadID INT IDENTITY(1,1) PRIMARY KEY,
        customerID INT NOT NULL,
        targetArea NVARCHAR(255) NOT NULL,
        businessName NVARCHAR(255) NOT NULL,
        businessIndustry NVARCHAR(255) NOT NULL,
        contactEmail NVARCHAR(255) NOT NULL,
        location NVARCHAR(255) NULL,
        phoneNumber NVARCHAR(50) NULL,
        description NVARCHAR(MAX) NULL,
        size NVARCHAR(50) NULL,
        website NVARCHAR(255) NULL
    );
    """)

    conn.commit()
    print("Table created successfully")

    cursor.close()