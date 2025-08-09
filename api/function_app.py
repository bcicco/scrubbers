import azure.functions as func
import datetime
import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

#load_dotenv() 


app = func.FunctionApp()

# Get API key from environment variables
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
print("OPENAI API KEY:", OPENAI_API_KEY)
@dataclass
class BusinessLead:
    """Data class to represent a business lead"""
    name: str
    industry: str
    contact_email: str
    location: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None

class Business(BaseModel):
    name: str
    industry: str
    contact_email: str
    location: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None

class Businesses(BaseModel):
    business_leads: List[Business]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'industry': self.industry,
            'location': self.location,
            'website': self.website,
            'contact_email': self.contact_email,
            'phone': self.phone,
            'description': self.description,
            'size': self.size
        }

class AnthropicClient:
    """Client for interacting with Anthropic API to find business leads"""
    
    def __init__(self, api_key: str):
        """
        Initialize the Anthropic client
        
        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key
        self.client = Anthropic(api_key=self.api_key)
        
    def _make_request(self, prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
        """
        Make a request to the Anthropic API
        
        Args:
            prompt: The prompt to send to the API
            model: The model to use for the request
            
        Returns:
            String containing the API response content
        """
        
        try:
            # Make the API call using Anthropic's format
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                temperature=0.3,
                system="You are a JSON ONLY API, that responds in only JSON",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 5
                    }
                ]
            )
            
            # Extract content from Anthropic's response format
            for content_block in reversed(response.content):
                if hasattr(content_block, 'type') and content_block.type == 'text':
                    return content_block.text
            else:
                return response.content[-1].text
            
        except Exception as e:
            print(f"Anthropic API request failed: {e}")
            raise
    
    def find_businesses(self, 
                       product: str, 
                       product_description: str,
                       target_industry: str, 
                       location: str = "", 
                       business_size: str = "small to medium",
                       num_businesses: int = 10) -> List[BusinessLead]:
        """
        Find businesses that might be interested in your product/service
        
        Args:
            product: Name of the product you're selling
            product_description: Description of what you're selling
            target_industry: Industry to target
            location: Geographic location (optional)
            business_size: Size of businesses to target
            num_businesses: Number of businesses to find
            
        Returns:
            List of BusinessLead objects
        """
        location_filter = f"must have a shop in {location}" if location else ""
        
        prompt = f"""
CRITICAL INSTRUCTION: Respond with ONLY valid JSON. No explanations, no introductions, no additional text.

Search the web to find the email addresses of {num_businesses} real businesses {location_filter} in the {target_industry} industry that would purchase {product}.

Product: {product}
Description: {product_description}

Use web search to find actual business email addresses with real contact information. Only include businesses if you find the email address.

RESPOND WITH ONLY THIS JSON FORMAT (no other text):
{{
    "businesses": [
        {{
            "name": "Actual Business Name Found Via Search",
            "industry": "Industry/sector",
            "contact_email": "email",
            "location": "City, State/Country",
            "website": "https://actualwebsite.com",
            "phone": "+61xxxxxxxxx",
            "description": "Brief description",
            "size": "small/medium"
        }}
    ]
}}

RULES:
- Use web search to find real businesses
- Extract real contact information from their websites
- Return ONLY the JSON object above
- No introductory text, explanations, or additional commentary
- Start your response immediately with the opening brace 
"""
        
        try:
            response_content = self._make_request(prompt)
            print(response_content)
            # Clean up the response to extract JSON
            # Remove any markdown formatting or extra text
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_content = response_content[json_start:json_end]
            else:
                json_content = response_content
            
            # Parse JSON response
            business_data = json.loads(json_content)
            
            # Convert to BusinessLead objects List
            businesses = []
            for biz in business_data.get('businesses', []):
                businesses.append(BusinessLead(
                    name=biz.get('name', ''),
                    industry=biz.get('industry', ''),
                    location=biz.get('location'),
                    website=biz.get('website'),
                    contact_email=biz.get('contact_email', ''),
                    phone=biz.get('phone'),
                    description=biz.get('description'),
                    size=biz.get('size')
                ))
            
            print(f"Successfully found {len(businesses)} businesses")
            return businesses
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response content: {response_content}")
            return []
        except Exception as e:
            print(f"Error finding businesses: {e}")
            return []

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def _make_request(self, prompt: str) -> str:
        try:
            response = self.client.responses.parse(
                model="gpt-4o",
                input=prompt,
                tools=[{"type": "web_search_preview", "search_context_size": "medium"}],
                text_format=Businesses
            )
            '''
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            '''
            print(response.usage)
            print(type(response.usage))
            print(response.usage.input_tokens)
            print(response.usage.output_tokens)

           
            token_details = {
                "prompt_tokens": 12,
                "completion_tokens": 12,
                "total_tokens": 12
            }
            return response.output_parsed, token_details
        except Exception as e:
            print(f"OpenAI Responses API request failed: {e}")
            raise

    def find_businesses(
        self,
        product: str,
        product_description: str,
        target_industry: str,
        location: str = "",
        business_size: str = "small to medium",
        num_businesses: int = 10
    ) -> Businesses:

        location_filter = f"must have a shop in {location}" if location else ""

        prompt = f"""
Using only 3 search queries, find {num_businesses} businesses that are not purely online, {location_filter} in the {target_industry} industry 
that would likely be interested in purchasing {product} from me. Ideally they will not already stock my product.
Here is a description of {product}: {product_description}



Make sure to ground your info using web search and include verified email addresses.
"""
        try:
            businesses, token_details = self._make_request(prompt)
            return businesses, token_details
        except Exception as e:
            print(f"Error during business search (OpenAI): {e}")
            return []


client = None
if ANTHROPIC_API_KEY:
    client = AnthropicClient(ANTHROPIC_API_KEY)

@app.route(route="test", auth_level=func.AuthLevel.ANONYMOUS)
def test(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.route(route="get_business_leads", auth_level=func.AuthLevel.ANONYMOUS)
def get_business_leads(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to generate business leads using Anthropic"""
    
    try:
        logging.info('Business leads function triggered')
        
        # Check if Anthropic client is initialized
        if not client:
            return func.HttpResponse(
                json.dumps({"error": "Anthropic API key not configured"}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Get parameters from query string
        locality = req.params.get('locality')
        product = req.params.get('product') 
        product_description = req.params.get('product_description')
        target_industry = req.params.get('target_industry')
        
        # Validate required parameters
        if not all([locality, product, product_description, target_industry]):
            missing_params = []
            if not locality: missing_params.append('locality')
            if not product: missing_params.append('product')
            if not product_description: missing_params.append('product_description')
            if not target_industry: missing_params.append('target_industry')
            
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required parameters",
                    "missing": missing_params,
                    "required": ["locality", "product", "product_description", "target_industry"]
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        logging.info(f"Generating leads for {product} in {locality}, targeting {target_industry}")
        
        # Generate business leads
        businesses = client.find_businesses(
            product=product,
            product_description=product_description,
            target_industry=target_industry,
            location=locality
        )
        
        # Return the results
        result = {
            "businesses": [b.to_dict() for b in businesses],
            "meta": {
                "product": product,
                "location": locality,
                "industry": target_industry,
                "count": len(businesses),
                "generated_at": datetime.datetime.utcnow().isoformat()
            }
        }
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in get_business_leads function: {e}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error", 
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
@app.route(route="get_business_leads_openai", auth_level=func.AuthLevel.ANONYMOUS)
def get_business_leads_openai(req: func.HttpRequest) -> func.HttpResponse:
    """GET route to generate leads using OpenAI"""
    openai_client = OpenAIClient(OPENAI_API_KEY)
    try:
        print("OpenAI business leads GET triggered")

        if not openai_client:
            return func.HttpResponse(
                json.dumps({"error": "OpenAI API key not configured"}),
                status_code=500,
                mimetype="application/json"
            )

        # Extract query parameters
        locality = req.params.get('locality')
        product = req.params.get('product')
        product_description = req.params.get('product_description')
        target_industry = req.params.get('target_industry')

        # Check for missing fields
        missing = []
        if not locality: missing.append("locality")
        if not product: missing.append("product")
        if not product_description: missing.append("product_description")
        if not target_industry: missing.append("target_industry")

        if missing:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required query parameters",
                    "missing": missing
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Get leads
        businesses, token_details = openai_client.find_businesses(
            product, product_description, target_industry, locality
        )

        result = {
            "businesses": [b.model_dump() for b in businesses.business_leads],
            "meta": {
                "product": product,
                "location": locality,
                "industry": target_industry,
                "count": len(businesses.business_leads),
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "token_details": token_details
            }
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Unexpected error in OpenAI business leads: {e}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
