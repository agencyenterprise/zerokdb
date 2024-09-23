from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///db.db"  # postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
session = SessionLocal()


class TableSequences(Base):
    __tablename__ = "table_sequences"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, index=True, nullable=False)
    cid = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)
