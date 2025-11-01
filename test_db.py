from sqlalchemy import create_engine
from models import Base
import os

engine = create_engine(os.getenv("DATABASE_URL"))
Base.metadata.create_all(engine)
print("Tables created!")