from typing import List
import pyodbc

def create_customer_registration_table(server_creds: List[str]):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
    CREATE TABLE Customer_Registration (
        Customer_ID INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(255) NOT NULL,
        Email_Address NVARCHAR(255) NOT NULL UNIQUE,
        Password NVARCHAR(255) NOT NULL
    );
    """)
    
    conn.commit()
    print("Customer Registration table created successfully")
    
    cursor.close()
    conn.close()

def create_product_registration_table(server_creds: List[str]):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
    CREATE TABLE Product_Registration (
        Product_ID INT IDENTITY(1,1) PRIMARY KEY,
        Customer_ID INT NOT NULL,
        Product_Name NVARCHAR(255) NOT NULL,
        Product_Desc NVARCHAR(MAX) NULL,
        Target_Industry NVARCHAR(255) NULL,
        Selected_Areas NVARCHAR(MAX) NULL,
        FOREIGN KEY (Customer_ID) REFERENCES Customer_Registration(Customer_ID)
    );
    """)
    
    conn.commit()
    print("Product Registration table created successfully")
    
    cursor.close()
    conn.close()

def create_business_registrar_table(server_creds: List[str]):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
    CREATE TABLE Business_Registrar (
        Contact_Email NVARCHAR(255) PRIMARY KEY,
        Business_Name NVARCHAR(255) NOT NULL,
        Opted_Out BIT DEFAULT 0,
        Currently_Contacting BIT DEFAULT 0,
    );
    """)
    
    conn.commit()
    print("Business Registrar table created successfully")
    
    cursor.close()
    conn.close()

def create_leads_table(server_creds: List[str]):
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    cursor.execute(
    """
    CREATE TABLE dbo.Leads (
        Lead_ID INT IDENTITY(1,1) PRIMARY KEY, -- Auto-increment PK
        Customer_ID INT NOT NULL,              -- FK to Customer_Registration
        Product_Id INT NOT NULL,               -- FK to Product_Registration
        Contact_Email NVARCHAR(255) NOT NULL,
        Business_Name NVARCHAR(255) NOT NULL,
        Business_Description NVARCHAR(MAX) NULL,
        Personalised_Statement NVARCHAR(MAX) NULL,
        Date_Found DATETIME NOT NULL DEFAULT GETDATE(),
        Status NVARCHAR(50) NULL,
        Last_Contact_Date DATETIME NULL,
        FOREIGN KEY (Customer_ID) REFERENCES Customer_Registration(Customer_ID),
        FOREIGN KEY (Product_Id) REFERENCES Product_Registration(Product_ID)
    );
    """)

    
    conn.commit()
    print("Leads table created successfully")
    
    cursor.close()
    conn.close()

def create_all_tables(server_creds: List[str]):
    """
    Creates all tables in the correct order to respect foreign key constraints.
    """
    try:
        #create_customer_registration_table(server_creds)
        #create_product_registration_table(server_creds)
        #create_business_registrar_table(server_creds)
        create_leads_table(server_creds)
        print("All tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")

