import hashlib
import json


class ChangeTracker:
    def __init__(self, log_file="change_log.json"):
        self.log_file = log_file
        self.changes = self._load_changes()

    def _load_changes(self):
        try:
            with open(self.log_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_changes(self):
        with open(self.log_file, "w") as file:
            json.dump(self.changes, file, indent=4)

    def _hash_data(self, data):
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def log_change(self, query, data):
        query_hash = self._hash_data(query)
        data_hash = self._hash_data(data)
        change_record = {
            "query_hash": query_hash,
            "query": query,
            "data_hash": data_hash,
        }
        self.changes.append(change_record)
        self._save_changes()
