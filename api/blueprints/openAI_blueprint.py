# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(openAI) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints


import azure.functions as func
import logging
from utils.database.push_leads_to_db import push_to_db
import os
import json
from utils.openAI import OpenAIClient

openAIBP = func.Blueprint()



@openAIBP.route(route="get_business_leads_openai", auth_level=func.AuthLevel.ANONYMOUS)
def get_business_leads_openai(req: func.HttpRequest) -> func.HttpResponse:
    """GET route to generate leads using OpenAI"""

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    server_creds = [
        "{ODBC Driver 17 for SQL Server}",
        "scrubbresdbserver.database.windows.net",
        "scrubbersdb",
        "bcicco",
        "Chinaroll1!",
    ]

    if OPENAI_API_KEY == None:
        return func.HttpResponse(
            json.dumps({"error": "OpenAI API key not configured"}),
            status_code=500,
            mimetype="application/json",
        )

    openai_client = OpenAIClient(OPENAI_API_KEY)
    try:
        print("OpenAI business leads GET triggered")

        # query params from get requests
        locality = req.params.get("locality")
        product = req.params.get("product")
        customer_id = req.params.get("customer_id")
        product_description = req.params.get("product_description")
        target_industry = req.params.get("target_industry")

        # debuggin --> checks for missing params, probably a better way to do this
        missing = []
        if not locality:
            missing.append("locality")
        if not product:
            missing.append("product")
        if not product_description:
            missing.append("product_description")
        if not target_industry:
            missing.append("target_industry")

        if missing:
            return func.HttpResponse(
                json.dumps(
                    {"error": "Missing required query parameters", "missing": missing}
                ),
                status_code=400,
                mimetype="application/json",
            )

        # Get leads
        businesses, token_details = openai_client.find_businesses(
            product, product_description, target_industry, locality
        )
        push_to_db(businesses, customer_id, locality, server_creds)

        return func.HttpResponse(
            "Open AI business leads obtained + pushed successfully",
            status_code=200,
        )

    except Exception as e:
        print(f"Unexpected error in OpenAI business leads: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
        )