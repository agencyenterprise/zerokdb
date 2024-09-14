from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from zerokdbapi.db import TableSequences, SessionLocal

def get_table_sequence_by_id(record_id: int):
    """
    Retrieve a record from the TableSequences model based on the given id.
    """
    session: Session = SessionLocal()
    try:
        record = session.query(TableSequences).filter(TableSequences.id == record_id).first()
        return record
    finally:
        session.close()
