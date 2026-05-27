class DebugCollector:
    """for collecting different metrics from every part of the game"""
    
    def __init__(self):
        self._data = {}
    
    def set(self, key: str, value):
        self._data[key] = value
    
    def get(self, key: str, default=None):
        return self._data.get(key, default)
    
    def get_all(self) -> dict:
        return self._data.copy()
    
    def clear(self):
        self._data.clear()
