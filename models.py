from sqlalchemy import Column, BigInteger, String
from database import Base

class PressList(Base):
    __tablename__ = "press_list"
    press_list_id = Column(BigInteger, primary_key=True, index=True)
    press_date = Column(String(20))
    press_url = Column(String(2000))
    company_name = Column(String(200))
    press_title = Column(String(2000))
