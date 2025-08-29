from typing import List
import pyodbc

def insert_customer(server_creds: List[str], name: str, email: str, password: str):
    """
    Insert a single customer into the Customer_Registration table
    """
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO Customer_Registration (Name, Email_Address, Password)
        VALUES (?, ?, ?)
        """, (name, email, password))
        
        conn.commit()
        
        cursor.execute("SELECT @@IDENTITY")
        customer_id = cursor.fetchone()[0]
        
        print(f"Customer '{name}' inserted successfully with ID: {customer_id}")
        return customer_id
        
    except pyodbc.IntegrityError as e:
        print(f"Error: Email address '{email}' already exists in the database.")
        return None
    except Exception as e:
        print(f"Error inserting customer: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()