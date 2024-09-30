from zerokdb.ipfs_storage import TableData
from datetime import datetime
from typing import List, Union, Tuple
import hashlib
from zerok.commitments.mkzg.ecc import curve_order
from zerok.circuits.circuit import LayeredCircuit
from zerok.graph.engine import Value
from zerok.prover.prover import ZkProver
from zerok.polynomials.field import SCALE
import random
from functools import reduce
import operator


def prod(iterable):
    return reduce(operator.mul, iterable, 1)


def hash_value(value: str):
    if isinstance(value, str):
        return int(hashlib.sha256(value.encode()).hexdigest(), 16)
    elif isinstance(value, int) or isinstance(value, float):
        return int(hashlib.sha256(str(value).encode()).hexdigest(), 16)
    elif isinstance(value, bool):
        return int(hashlib.sha256(str(value).encode()).hexdigest(), 16)
    elif isinstance(value, datetime):
        return int(hashlib.sha256(str(value.timestamp()).encode()).hexdigest(), 16)


def hash_table_column(
    column_name: str, column_type: str, column_value: str, column_index: str
):
    value = 0
    if column_type == "string":
        if not isinstance(column_value, str):
            raise ValueError("Expected string value")
        value = int(column_value.encode("utf-8").hex(), 16)
    elif column_type == "int":
        if not isinstance(column_value, int):
            raise ValueError("Expected int value")
        value = column_value
    elif column_type == "float":
        if not isinstance(column_value, float):
            raise ValueError("Expected float value")
        value = int(round(column_value * 1e8), 0)
    elif column_type == "bool":
        if not isinstance(column_value, bool):
            raise ValueError("Expected bool value")
        value = int(column_value)
    elif column_type == "datetime":
        if not isinstance(column_value, datetime):
            raise ValueError("Expected datetime value")
        value = int(column_value.timestamp())
    elif column_type == "list[float]":
        if not isinstance(column_value, list):
            raise ValueError("Expected list value")
        value = int(hashlib.sha256(str(column_value).encode()).hexdigest(), 16)
    else:
        raise ValueError("Unsupported column type")
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
    circuit = generate_circuit_for_proof_of_membership(table, records, where_columns)
    prover = ZkProver(circuit)
    assert prover.prove(), "Proof of membership failed"
    return circuit, prover.proof_transcript.to_bytes()
