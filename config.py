import json
from pathlib import Path


class Config:
    region = None
    config = None
    project_root = Path(__file__).parent
    config_file = project_root.joinpath("config.json")

    def __init__(self, env: str, service: str):
        self.env = env
        self.service = service
        self.set_config_file()
        self.set_region()

    def set_config_file(self):
        """
        Load the config file located in the root of this project.
        :return: config data
        """
        with open(self.config_file) as f:
            self.config = json.load(f)

    def set_region(self):
        self.region = self.config[self.env]["region"]
