from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    raw_message = Column(String)
    parsed_data = Column(JSON)
    score = Column(Float)
    suggested_action = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Later: engine, Session