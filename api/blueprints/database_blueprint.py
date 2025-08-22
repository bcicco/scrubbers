from utils.database.instantiate_table import create_SQL_table
from utils.database.pull_contact_emails import get_email_addresses
import azure.functions as func
import json

databaseBP = func.Blueprint()


@databaseBP.route(route="create_leads_table", auth_level=func.AuthLevel.ANONYMOUS)
def create_leads_table(req: func.HttpRequest) -> func.HttpResponse:
    server_creds = [
        "{ODBC Driver 17 for SQL Server}",
        "scrubbresdbserver.database.windows.net",
        "scrubbersdb",
        "bcicco",
        "Chinaroll1!",
    ]
    try:
        create_SQL_table(server_creds)
        return func.HttpResponse(
            "This HTTP triggered function executed successfully", status_code=200
        )
    except Exception as e:
        print(f"Unexpected error in creating table: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
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