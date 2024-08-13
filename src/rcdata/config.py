"""
...
"""
from .base import BaseData

class ConfigData(BaseData):
    def __init__(self, defaults: dict, config_path: str):
        super().__init__(defaults)
        self.config_path = config_path
        self.load()

    def load(self):
        try:
            super().load(self.config_path, compact = False)
        except FileNotFoundError:
            pass

    def sync(self):
        return super().sync(self.config_path, compact= False)
