import asyncio
import json
from services.hub_service import call_hub_get, call_hub_post
from services.proof_service import generate_proof
import base64
import dill

def process_designated_proof_requests(signature_message_id: bytes, signature: str, pinata_api_key: str):
    print("Fetching designated proof requests...")

    try:
        proof_request = call_hub_get(
            "/proof_requests/designated",
            {
                "signature-message-id": signature_message_id,
                "signature": signature,
            },
        )

        if not proof_request:
            print("No proof request to process.")
            return

        print("Processing proof request ", proof_request["id"])

        call_hub_post(
            "/proof_requests/acknowledge/" + proof_request["id"],
            {},
            {
                "signature-message-id": signature_message_id,
                "signature": signature,
            },
        )

        circuit, proof, result = asyncio.run(
            generate_proof(
                proof_request["id"],
                proof_request["ai_model_name"],
                proof_request["ai_model_inputs"],
                pinata_api_key,
            )
        )

        b64_circuit = base64.b64encode(dill.dumps(circuit)).decode() if circuit else ""
        b64_proof = base64.b64encode(proof).decode() if proof else ""

        call_hub_post(
            "/proof_requests/proof/" + proof_request["id"],
            {
                "circuit": b64_circuit,
                "proof": b64_proof,
                "ai_model_output": json.dumps(result or []),
            },
            {
                "signature-message-id": signature_message_id,
                "signature": signature,
            },
        )
    except Exception as e:
        print("Error processing proof requests: ", e)
