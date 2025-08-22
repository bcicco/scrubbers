import azure.functions as func
from dotenv import load_dotenv
from blueprints.openAI_blueprint import openAIBP
from blueprints.database_blueprint import databaseBP
"""Uncomment below for Local Dev"""
#load_dotenv()

# Instantiate App
app = func.FunctionApp()
app.register_functions(openAIBP)
app.register_functions(databaseBP)

