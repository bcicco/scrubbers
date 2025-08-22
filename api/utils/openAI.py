
from openai import OpenAI
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

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


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def _make_request(self, prompt: str) -> str:
        try:
            response = self.client.responses.parse(
                model="gpt-5-mini",
                input=prompt,
                tools=[{"type": "web_search_preview", "search_context_size": "high"}],
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
Find as many emails as possible emails of businesses that are not purely online, {location_filter} in the {target_industry} industry 
that would likely be interested in purchasing {product} from me. Ideally they will not already stock my product.
Here is a description of {product}: {product_description}



Make sure to ground your info using web search and only include businesses with email addresses. If you do not explicitly find the email address, fill in the email field with: Not available. Note that {location} is in Australia.
"""
        try:
            businesses, token_details = self._make_request(prompt)
            return businesses, token_details
        except Exception as e:
            print(f"Error during business search (OpenAI): {e}")
            return []