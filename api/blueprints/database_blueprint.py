from utils.database.instantiate_db import create_all_tables
from utils.database.pull_contact_emails import get_email_addresses
from utils.database.customer_table import insert_customer
from utils.database.product_table import insert_product
import azure.functions as func
import json

databaseBP = func.Blueprint()


@databaseBP.route(route="create_tables", auth_level=func.AuthLevel.ANONYMOUS)
def instantiate_database(req: func.HttpRequest) -> func.HttpResponse:
    server_creds = [
        "{ODBC Driver 17 for SQL Server}",
        "scrubbresdbserver.database.windows.net",
        "scrubbersdb",
        "bcicco",
        "Chinaroll1!",
    ]
    try:
        create_all_tables(server_creds)
        return func.HttpResponse(
            "This HTTP triggered function executed successfully", status_code=200
        )
    except Exception as e:
        print(f"Unexpected error in creating tables: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
    
@databaseBP.route(route="create_customer", auth_level=func.AuthLevel.ANONYMOUS)
def create_customer(req: func.HttpRequest) -> func.HttpResponse:
    server_creds = [
        "{ODBC Driver 17 for SQL Server}",
        "scrubbresdbserver.database.windows.net",
        "scrubbersdb",
        "bcicco",
        "Chinaroll1!",
    ]
    name = req.params.get('name')
    email = req.params.get('email')
    password = req.params.get('password')
    try:
        insert_customer(server_creds, name, email, password)
        return func.HttpResponse(
            "This HTTP triggered function executed successfully", status_code=200
        )
    except Exception as e:
        print(f"Unexpected error in updating table: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
        )

@databaseBP.route(route="create_product", auth_level=func.AuthLevel.ANONYMOUS)
def create_product(req: func.HttpRequest) -> func.HttpResponse:
    server_creds = [
        "ODBC Driver 17 for SQL Server",
        "scrubbresdbserver.database.windows.net",
        "scrubbersdb",
        "bcicco",
        "Chinaroll1!",
    ]
    
    try:
        # Get parameters from query string or request body
        customer_id = req.params.get('customer_id')
        product_name = req.params.get('product_name')
        product_desc = req.params.get('product_desc')
        target_industry = req.params.get('target_industry')
        selected_areas = req.params.get('selected_areas')
        
        # Try request body if not in query params
        if not all([customer_id, product_name]):
            try:
                req_body = req.get_json()
                if req_body:
                    customer_id = customer_id or req_body.get('customer_id')
                    product_name = product_name or req_body.get('product_name')
                    product_desc = product_desc or req_body.get('product_desc')
                    target_industry = target_industry or req_body.get('target_industry')
                    selected_areas = selected_areas or req_body.get('selected_areas')
            except ValueError:
                pass
        
        # Validate required parameters
        if not customer_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameter: customer_id"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if not product_name:
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameter: product_name"}),
                status_code=400,
                mimetype="application/json"
            )
        
        try:
            customer_id = int(customer_id)
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "customer_id must be a valid integer"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Insert product
        product_id = insert_product(server_creds, customer_id, product_name.strip(), 
                                  product_desc, target_industry, selected_areas)
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Product created successfully",
                "product_id": product_id,
                "customer_id": customer_id,
                "product_name": product_name.strip()
            }),
            status_code=201,
            mimetype="application/json"
        )
        
    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        print(f"Unexpected error in create_product: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
    

    
@databaseBP.route(route="pull_contact_emails", auth_level=func.AuthLevel.ANONYMOUS)
def pull_contact_emails(req: func.HttpRequest) -> func.HttpResponse:
    customer_id = req.params.get('customer_id')
    server_creds = [
        "{ODBC Driver 17 for SQL Server}",
        "scrubbresdbserver.database.windows.net",
        "scrubbersdb",
        "bcicco",
        "Chinaroll1!",
    ]

    try:
        emails = get_email_addresses(server_creds, customer_id)
        return func.HttpResponse(
            json.dumps({"customer_id": customer_id, "emails": emails}),
            status_code=200,
            mimetype="application/json",
        )
     
    except Exception as e:
        print(f"Unexpected error in pulling emails: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
        )