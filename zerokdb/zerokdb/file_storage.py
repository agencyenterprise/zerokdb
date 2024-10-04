import json


class FileStorage:
    def __init__(self, filename):
        self.filename = filename

    def save(self, data, entity_id):
        with open(self.filename, "w") as file:
            json.dump(data, file)
        return {}

    def create_table(self, entity_name, data):
        with open(self.filename, "w") as file:
            json.dump(data, file)
        return {}

    def load(self, cid: str):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
