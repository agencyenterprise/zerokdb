import hashlib
import operator
import random
import sys
from datetime import datetime
from functools import reduce
from typing import List, Tuple, Union

from zerok.circuits.circuit import LayeredCircuit
from zerok.commitments.mkzg.ecc import curve_order
from zerok.graph.engine import Value
from zerok.polynomials.field import SCALE
from zerok.prover.prover import ZkProver

from zerokdb.ipfs_storage import TableData

sys.set_int_max_str_digits(100000)


def prod(iterable):
    return reduce(operator.mul, iterable, 1)


def hash_value(value: Union[str, int, float, bool, datetime]) -> int:
    if isinstance(value, str):
        return int(hashlib.sha256(value.encode()).hexdigest(), 16)
    elif isinstance(value, (int, float)):
        return int(hashlib.sha256(str(value).encode()).hexdigest(), 16)
    elif isinstance(value, bool):
        return int(hashlib.sha256(str(value).encode()).hexdigest(), 16)
    elif isinstance(value, datetime):
        return int(hashlib.sha256(str(value.timestamp()).encode()).hexdigest(), 16)
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")


def hash_table_column(
    column_name: str,
    column_type: str,
    column_value: Union[str, int, float, bool, datetime, List[float]],
    column_index: int,
) -> int:
    type_handlers = {
        "STRING": lambda x: int.from_bytes(x.encode("utf-8"), "big"),
        "TEXT": lambda x: int.from_bytes(x.encode("utf-8"), "big"),
        "INT": lambda x: x,
        "FLOAT": lambda x: int(round(x * 1e8)),
        "BOOL": int,
        "DATETIME": lambda x: int(x.timestamp()),
        "LIST[FLOAT]": lambda x: int.from_bytes(
            hashlib.sha256(str(x).encode()).digest(), "big"
        ),
    }

    if column_type not in type_handlers:
        raise ValueError(f"Unsupported column type: {column_type}")

    if not isinstance(column_value, type(column_value).__mro__[0]):
        raise ValueError(f"Expected {column_type} value, got {type(column_value)}")

    value = type_handlers[column_type](column_value)
    column_id = hash_value(column_name)
    value = hash_value(str(column_id) + str(column_index) + str(value))
    return value % curve_order


def table_to_polynomial(table: TableData) -> List[int]:
    """Decomposes table into polynomials.

    Args:
        table (TableData): A table data.

    Returns:
        List[int]: A list of array where each item is a root of the polynomial.
    """
    columns = table["columns"]
    column_types = table["column_types"]
    rows = table["rows"]
    polynomials = []
    for row in rows:
        for i, (column_name, column_value) in enumerate(zip(columns, row)):
            column_type = column_types[column_name]
            value = hash_table_column(column_name, column_type, column_value, i)
            polynomials.append(value)
    return polynomials


def record_to_polynomial(
    records: List[List[Union[int, str, List[float]]]],
    table: TableData,
    where_columns: List[str],
) -> List[int]:
    """Decomposes records into polynomials.
    Args:
        records (List[List[Union[int, str, List[float]]]): A list of records.
        table (TableData): A table data.
        where_columns (List[str]): A list of columns to be used in the where clause.
    Returns:
        List[int]: A list of array where each item is a root of the polynomial.
    """
    columns = table["columns"] if not where_columns else where_columns
    column_types = table["column_types"]
    polynomial = []
    for record in records["rows"]:
        for i, (column_name, column_value) in enumerate(zip(columns, record)):
            if column_name == "*":
                # Skip the '*' column as it's not a real column
                continue
            column_type = column_types[column_name]
            value = hash_table_column(column_name, column_type, column_value, i)
            polynomial.append(value)
    return polynomial


def generate_circuit_for_proof_of_membership(
    table: TableData,
    records: List[List[Union[int, str, List[float]]]],
    where_columns: List[str],
) -> LayeredCircuit:
    random_integer = random.randint(0, curve_order)
    if not table:
        table_product = 1
    else:
        table_polynomials = [x for x in table_to_polynomial(table)]
        table_evaluations = [random_integer - x for x in table_polynomials]
        table_product = prod(table_evaluations)
    if not records:
        record_product = 1
    else:
        record_polynomials = [
            x for x in record_to_polynomial(records, table, where_columns)
        ]
        record_evaluations = [random_integer - x for x in record_polynomials]
        record_product = prod(record_evaluations)

    # @TODO: This is just an example on how to generate the proof. Given the constraints
    # for the hackathon we did not implemented all the steps for verifying the proof.
    # The ideal verifier should have a copy of the table_polynomials list
    # and should be able to verify the proof using it.
    # Additionaly the proof above only checks if there's records to be returned.
    # When there's no record to be returned there's no proof being generated, which is
    # not ideal. The proof should be generated regardless of the records being returned, but
    # we decied to keep it simple for the hackathon.
    quotient = table_product // record_product
    witness = Value(table_product % SCALE, integer=False) - Value(
        (record_product * quotient) % SCALE, integer=False
    )
    # @NOTE: The proof is based on the construction of a computational graph that checks if
    # the witness is equal to the product of the record evaluations, assuming the rest is zero.
    # A random challenge is generated and the prover proves that the witness is equal to the
    # polynomial constructed based on the table_product, quotient and record_product.
    # Ideally a transcript (using fiat shamir) should be used to generate deterministic
    # randmoness to proof the relation on line 129 holds based on the validity of
    # the Schwartz-Zippel lemma. We decided to keep it simple for the hackathon, as
    # we think that designing the concept is more important than the actual implementation, at least for now.
    circuit, _, layers = Value.compile_layered_circuit(witness, True)
    return circuit


def generate_proof_of_membership(
    table: TableData,
    records: List[List[Union[int, str, List[float]]]],
    where_columns: List[str],
) -> Tuple[LayeredCircuit, bytes]:
    try:
        circuit = generate_circuit_for_proof_of_membership(
            table, records, where_columns
        )
        prover = ZkProver(circuit)
        assert prover.prove(), "Proof of membership failed"
        return circuit, prover.proof_transcript.to_bytes()
    except Exception:
        return None, None
