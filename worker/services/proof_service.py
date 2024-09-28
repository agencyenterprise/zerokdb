from zerokdb.api import DatabaseAPI
import json


async def generate_proof(proof_request_id: str, ai_model_name: str, ai_model_inputs: str):
  print('Generating proof for request ' + proof_request_id)
  result = None

  if ai_model_name != 'zerokdb':
    return None, None

  db_api = DatabaseAPI(storage_type='ipfs') # TODO change for being IPFS

  print('AI model inputs: ' , ai_model_inputs)

  ai_model_inputs_dict = json.loads(ai_model_inputs)

  if ai_model_inputs_dict['type'] == 'TEXT':
      print('if tEXT ENTROU' )
      result = db_api.convert_text_to_embedding(ai_model_inputs_dict['value'])
  elif ai_model_inputs_dict['type'] == 'SQL':
      print('if SQL ENTROU' )
      result = db_api.execute_query(ai_model_inputs_dict['value'])
  else:
      raise ValueError("Unsupported AI model input type")

  print('result', result)

  circuit = "To be Done" # TODO LOLO to change this for the proof generation
  proof = "To be Done"

  print('Proof generated for request ' + proof_request_id)

  return circuit, proof, result