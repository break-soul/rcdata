
from .base import BaseData

class ResourceData(BaseData):
    def __init__(self, defaults: dict, resource_path: str):
        super().__init__(defaults)
        self.resource_path = resource_path
        self.load()

    def load(self):
        try:
            super().load(self.resource_path, compact = False)
        except FileNotFoundError:
            pass

    def sync(self):
        return super().sync(self.resource_path, compact= False)

class ResourceIndex(BaseData):
    def __init__(self, defaults: dict, index_path: str):
        super().__init__(defaults)
        self.index_path = index_path
        self.load()

    def load(self):
        try:
            super().load(self.index_path, compact = False)
        except FileNotFoundError:
            pass

    def sync(self):
        return super().sync(self.index_path, compact= False)
