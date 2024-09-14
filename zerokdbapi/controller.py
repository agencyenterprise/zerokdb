def add_table_sequence(table_name: str, cid: str) -> TableSequences:
    """
    Add a new record to the TableSequences model.
    """
    session: Session = SessionLocal()
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
