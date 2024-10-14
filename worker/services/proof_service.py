import os
from zerokdb.api import DatabaseAPI
import json

api_host=os.getenv("API_HOST") or "https://kumh6ogteddmj4pgtuh7p00k9c.ingress.akash-palmito.org"

async def generate_proof(
    proof_request_id: str, ai_model_name: str, ai_model_inputs: str, pinata_api_key: str
):
    print("Generating proof for request " + proof_request_id)
    result = None

    if ai_model_name != "zerokdb":
        return None, None

    try:
        db_api = DatabaseAPI(storage_type="ipfs", pinata_api_key=pinata_api_key, api_host=api_host)
        ai_model_inputs_dict = json.loads(ai_model_inputs)

        if ai_model_inputs_dict["type"] == "TEXT":
            text = ai_model_inputs_dict["value"]["text"]
            table_name = ai_model_inputs_dict["value"]["table_name"]
            vector = db_api.convert_text_to_embedding(text)
            sql_query = f"SELECT * FROM {table_name} LIMIT 5 COSINE SIMILARITY embedding WITH {vector}"
        elif ai_model_inputs_dict["type"] == "SQL":
            sql_query = ai_model_inputs_dict["value"]
        else:
            raise ValueError("Unsupported AI model input type")

        result, circuit, proof = db_api.execute_query(sql_query, proof=True)
    except Exception as e:
        print("Error generating proof: ", e)
        return None, None, [["An error occurred while executing the query"]]

    print("Proof generated for request: ", proof_request_id)
    return circuit, proof, result
