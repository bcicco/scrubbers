from typing import List
import pyodbc

def insert_business(server_creds, email, name, opted_out, contacting):
    conn = pyodbc.connect(
    f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Business_Registrar (
            Contact_Email,
            Business_Name,
            Opted_Out,
            Currently_Contacting
        )
        VALUES (?, ?, ?, ?);
    """, (
        email,
        name,
        opted_out,   # Opted_Out
        contacting    # Currently_Contacting
    ))

def insert_business(server_creds, email, name, opted_out, contacting):
    conn = pyodbc.connect(
    f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Business_Registrar (
            Contact_Email,
            Business_Name,
            Opted_Out,
            Currently_Contacting
        )
        VALUES (?, ?, ?, ?);
    """, (
        email,
        name,
        opted_out,   # Opted_Out
        contacting    # Currently_Contacting
    ))

def opt_out_business(server_creds, email):
    conn = pyodbc.connect(
    f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE Business_Registrar
    SET Opted_Out = 1
    WHERE Contact_Email = ?;
""", (email,))

   