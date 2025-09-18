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