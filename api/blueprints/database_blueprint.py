# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(database) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints

from utils.database.instantiate_table import create_SQL_table
import azure.functions as func
import logging
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