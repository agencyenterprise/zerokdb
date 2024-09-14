from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TableSequences(Base):
    __tablename__ = "table_sequences"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, index=True)
    cid = Column(String, index=True)

Base.metadata.create_all(bind=engine)
