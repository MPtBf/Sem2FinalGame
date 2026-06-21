class DebugCollector:
    """for collecting different metrics from every part of the game"""
    
    def __init__(self):
        self._data = {}
    
    def set(self, key: str, value):
        # round first
        round_digits = 3
        if isinstance(value, float):
            value = round(value, round_digits)
        elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            value = [round(v, round_digits) if isinstance(v, float) else v for v in value]
        
        self._data[key] = value
    
    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def increase(self, key: str, value: int):
        self.set(key, self.get(key, 0) + value)
    
    def get_all(self) -> dict:
        return self._data.copy()
    
    def clear(self):
        self._data.clear()
