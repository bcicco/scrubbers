
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional

class Business(BaseModel):
    name: str
    industry: str
    contact_email: str
    location: Optional[str] = None
    #phone: Optional[str] = None
    description: Optional[str] = None
    #size: Optional[str] = None
    website: Optional[str] = None
    personalised_statement: Optional[str] = None
    #review: Optional[str] = None

    
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
                tools=[{"type": "web_search_preview", "search_context_size": "low"}],
                text_format=Businesses
            )
            '''
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            '''


           
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
        product: str ,
        product_description: str,
        target_industry: str,
        location: str,
        ethos: str

    ) -> Businesses:


        prompt = f"""

You are an API that responds in JSON format capable of finding the contact email of businesses according to a set of criteria so I can contact them about my new product. Below is the criteria you must adhere to:
    1. The businesses must have a real place of business (i.e not purely online) in {location}, Australia.
    2. The businesses must be in a specific industry. Here are some guidelines: {target_industry}
    3. The businesses must be a good fit for my new product: {product}. Here is a description so you can understand my product better: {product_description}.
    4. The businesses must not be part of a franchise or chain. 
    5. The businesses must not be permanently closed.
    6. To prove that the business is still open, you must find their website, not a business listings site.
    7. You are expected to return an exhausitive list of businesses. Cap the maximum number of businesses at 10.
Remember, you are primarily tasked with finding the email addresses of these businesses, however, I will ask you to return the following fields for each business: 
    - Name: The name of the business 
    - Industry: The industry the business belongs to
    - Contact Email: The contact email of the business, your primary objective
    - Location: The town or suburb where the business is located
    - Description: A 2 - 3 sentence describing key features of the business
    - Website: The website from which you sourced the contact email, should be the businesses official website.
    - Personalised statement: Craft an ethos match written in first person as if you are me, the owner of {product} that I am trying to sell. Maximum of three sentences. Beginning with 'I have chosen (found business name) because...', skipping an introduction as I have this covered. The statement should allign the identified businesses ethos with my companies ethos. This must be tailored to the identified businesses values, no assumptions. Do not include any extra text or citations, just the statement so I can copy and paste it straight into an email. Here is a description of my ethos to assist you: {ethos}
    - Review: A verfied review of the business found online. 


Make sure to ground your info using web search and only include businesses with email addresses. If you do not explicitly find the email address, fill in the email field with: Not available. Note that {location} is in Australia.
"""
        try:
            businesses, token_details = self._make_request(prompt)
            return businesses, token_details
        except Exception as e:
            print(f"Error during business search (OpenAI): {e}")
            return []
    




if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import os
    open_ai_key = os.getenv("OPENAI_API_KEY")
    localities = ["Essendon", "Moonee Ponds", "Flemington", "Ascot Vale", "Brunswick", "Pascoe Vale", "Carlton", "Collingwood", "Hawthorn", "Richmond", "Cremorne", "Fitzroy"]
    product = "Randall’s Coconut and Cellulose Sponge"
    product_description = "Randall’s Coconut and cellulose sponge is a kitchen/dish sponge. It is 100% plastic free. With the top made of abrasive but scratch free coconut fibres and a cellulose (wood pulp) sponge bottom. It is targeted for people who want: Plastic free kitchen for health reasons i.e not to get get microplastics in theirs or their families bodies. People who don’t want to contribute to polluting the environment with more plastic. People who are sick of cheap plastic and want something more premium "
    target_industry = "We are targetting grocers that specialise in organic / ecofriendly products. We are trying to avoid cafes that only sell hospitality style sit down meals, however, stores with an attached cafe is ok."
    ethos = "My business ethos: eco-friendly, Plastic free, Health conscious, Honest, Trustworthy, Environmentally friendly, Family oriented"
    client = OpenAIClient(open_ai_key)
    with open("business_leads.txt", "w", encoding="utf-8") as f:
        for locality in localities:
            businesses, token_details = client.find_businesses(
                product, product_description, target_industry, locality, ethos
            )

            for business in businesses.business_leads:
                f.write("*********************************\n")
                f.write(f"{business.name}\n")
                f.write("----------------------------------\n")
                f.write(f"{business.personalised_statement}\n")
                f.write("-----------------------------------\n")
                f.write(f"{business.contact_email}\n")
                f.write("--------------------------------------\n")

            f.write(f"FINAL COUNT ({locality}): {len(businesses.business_leads)}\n\n")
        print("FINAL COUNT: ", len(businesses.business_leads))
