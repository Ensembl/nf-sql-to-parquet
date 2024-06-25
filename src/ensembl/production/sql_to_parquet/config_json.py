import json

class Config:
    def __init__(self, json):
        self.json = json
    
    def config_query(self):
        with open(self.json, "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            optional_keys = ["supplementary_data", "lookup_key"]
            for k in optional_keys:
                if not k in data:
                    data[k] = None
        return data