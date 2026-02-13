from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://campaigns:campaigns@localhost:5432/campaigns"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

