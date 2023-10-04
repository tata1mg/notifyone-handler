import json


class Config:
    @staticmethod
    def json_file_to_dict(file: str) -> dict:
        config = None
        with open(file) as config_file:
            config = json.load(config_file)
        return config

    @staticmethod
    def get_config():
        return Config.json_file_to_dict("./config.json")
