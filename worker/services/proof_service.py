
from zerokdb.api import DatabaseAPI

def generate_proof(proof_request_id: str, ai_model_name: str, ai_model_inputs: str):
  print('Generating proof for request ' + proof_request_id)

  if ai_model_name != 'zerokdb':
    return None, None


  db_api = DatabaseAPI()


  # db_api.create_table(
  #   'users',
  #   {'id': 'int', 'name': 'string'}
  # )

  # db_api.insert_into(
  #   'users',
  #   {'id': 1, 'name': 'Alice'}
  # )

  # return

  if ai_model_inputs['type'] == 'TEXT':
      result = db_api.convert_text_to_embedding(ai_model_inputs['value'])
  elif ai_model_inputs['type'] == 'SQL':
      result = db_api.execute_query(ai_model_inputs['value'])
  else:
      raise ValueError("Unsupported AI model input type")
  print(result)

  circuit = "To be Done"
  proof = "To be Done"

  print('Proof generated for request ' + proof_request_id)

  return circuit, proof

generate_proof('1', 'zerokdb', {'type': 'SQL', 'value': 'SELECT * FROM users WHERE name = \'Alice\''})