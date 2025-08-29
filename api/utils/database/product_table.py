
import json
import azure.functions as func
from typing import List, Optional, Union
import pyodbc

def insert_product(server_creds: List[str], customer_id: int, product_name: str, 
                  product_desc: Optional[str] = None, target_industry: Optional[str] = None, 
                  selected_areas: Optional[Union[str, List[str]]] = None):
    """
    Insert a new product into the Product_Registration table
    """
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    try:
        # Check if customer exists
        cursor.execute("SELECT COUNT(*) FROM Customer_Registration WHERE Customer_ID = ?", (customer_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Customer with ID {customer_id} does not exist")
        
        # Convert selected_areas to JSON string if it's a list
        areas_json = None
        if isinstance(selected_areas, list):
            areas_json = json.dumps(selected_areas)
        elif isinstance(selected_areas, str) and selected_areas.strip():
            areas_json = selected_areas
        
        # Ensure all parameters have proper values (no None for required fields)
        product_desc = product_desc if product_desc else ""
        target_industry = target_industry if target_industry else ""
        
        # Debug logging
        print(f"Inserting product with params:")
        print(f"  customer_id: {customer_id} (type: {type(customer_id)})")
        print(f"  product_name: {product_name} (type: {type(product_name)})")
        print(f"  product_desc: {product_desc} (type: {type(product_desc)})")
        print(f"  target_industry: {target_industry} (type: {type(target_industry)})")
        print(f"  areas_json: {areas_json} (type: {type(areas_json)})")
        
        # Insert product with explicit parameter handling
        cursor.execute("""
        INSERT INTO Product_Registration (Customer_ID, Product_Name, Product_Desc, Target_Industry, Selected_Areas)
        VALUES (?, ?, ?, ?, ?)
        """, customer_id, product_name, product_desc, target_industry, areas_json)
        
        conn.commit()
        
        cursor.execute("SELECT @@IDENTITY")
        product_id = int(cursor.fetchone()[0])
        
        print(f"Product inserted successfully with ID: {product_id}")
        return product_id
        
    except pyodbc.IntegrityError as e:
        print(f"Integrity error: {e}")
        raise ValueError(f"Database constraint error: {str(e)}")
    except Exception as e:
        print(f"Database error details: {e}")
        raise Exception(f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def update_product(server_creds: List[str], product_id: int, product_name: Optional[str] = None, 
                  product_desc: Optional[str] = None, target_industry: Optional[str] = None, 
                  selected_areas: Optional[str] = None):
    """
    Update an existing product in the Product_Registration table
    """
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Product_Registration WHERE Product_ID = ?", (product_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        # Build dynamic update query based on provided parameters
        update_fields = []
        update_values = []
        
        if product_name is not None:
            update_fields.append("Product_Name = ?")
            update_values.append(product_name)
        
        if product_desc is not None:
            update_fields.append("Product_Desc = ?")
            update_values.append(product_desc)
        
        if target_industry is not None:
            update_fields.append("Target_Industry = ?")
            update_values.append(target_industry)
        
        if selected_areas is not None:
            update_fields.append("Selected_Areas = ?")
            update_values.append(selected_areas)
        
        if not update_fields:
            raise ValueError("No fields provided to update")
        
        # Add product_id to the end for the WHERE clause
        update_values.append(product_id)
        
        update_query = f"""
        UPDATE Product_Registration 
        SET {', '.join(update_fields)}
        WHERE Product_ID = ?
        """
        
        cursor.execute(update_query, update_values)
        conn.commit()
        
        rows_affected = cursor.rowcount
        if rows_affected > 0:
            print(f"Product with ID {product_id} updated successfully")
            return True
        else:
            print(f"No changes made to product with ID {product_id}")
            return False
        
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_product(server_creds: List[str], product_id: int):
    """
    Get a product by ID
    """
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT Product_ID, Customer_ID, Product_Name, Product_Desc, Target_Industry, Selected_Areas
        FROM Product_Registration 
        WHERE Product_ID = ?
        """, (product_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                "product_id": row[0],
                "customer_id": row[1],
                "product_name": row[2],
                "product_desc": row[3],
                "target_industry": row[4],
                "selected_areas": row[5]
            }
        else:
            return None
        
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_products_by_customer(server_creds: List[str], customer_id: int):
    """
    Get all products for a specific customer
    """
    conn = pyodbc.connect(
        f'DRIVER={server_creds[0]};SERVER={server_creds[1]};DATABASE={server_creds[2]};UID={server_creds[3]};PWD={server_creds[4]};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT Product_ID, Customer_ID, Product_Name, Product_Desc, Target_Industry, Selected_Areas
        FROM Product_Registration 
        WHERE Customer_ID = ?
        ORDER BY Product_ID
        """, (customer_id,))
        
        products = []
        for row in cursor.fetchall():
            products.append({
                "product_id": row[0],
                "customer_id": row[1],
                "product_name": row[2],
                "product_desc": row[3],
                "target_industry": row[4],
                "selected_areas": row[5]
            })
        
        return products
        
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


