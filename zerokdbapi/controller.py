from sqlalchemy.exc import SQLAlchemyError
from db import TableSequences, session
from typing import Optional


def add_table_sequence(table_name: str, cid: Optional[str] = None) -> TableSequences:
    """
    Add a new record to the TableSequences model.
    """
    try:
        new_record = TableSequences(table_name=table_name, cid=cid)
        session.add(new_record)
        session.commit()
        session.refresh(new_record)
        return new_record
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


def update_table_sequence_cid(record_id: int, new_cid: str) -> TableSequences:
    """
    Update the CID for a given record in the TableSequences model.
    """
    try:
        record = (
            session.query(TableSequences).filter(TableSequences.id == record_id).first()
        )
        if not record:
            raise ValueError(f"Record with id {record_id} not found.")

        record.cid = new_cid
        session.commit()
        session.refresh(record)
        return record
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_table_sequence_by_id(record_id: int) -> TableSequences:
    """
    Retrieve a record from the TableSequences model by its ID.
    """
    try:
        record = (
            session.query(TableSequences).filter(TableSequences.id == record_id).first()
        )
        if not record:
            raise ValueError(f"Record with id {record_id} not found.")
        return record
    except SQLAlchemyError as e:
        raise e
    finally:
        session.close()


def get_table_sequence_by_table_name(table_name: str) -> TableSequences:
    """
    Retrieve a record from the TableSequences model by its ID.
    """
    try:
        record = (
            session.query(TableSequences)
            .filter(TableSequences.table_name == table_name)
            .filter(TableSequences.cid is not None)
            .first()
        )
        return record
    except SQLAlchemyError as e:
        raise e
    finally:
        session.close()
