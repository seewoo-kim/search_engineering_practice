from typing import Optional
from pydantic import BaseModel

class PressListResponse(BaseModel):
    press_list_id: int
    press_date: Optional[str]
    press_url: Optional[str]
    company_name: Optional[str]
    press_title: Optional[str]

    class Config:
        from_attributes = True
