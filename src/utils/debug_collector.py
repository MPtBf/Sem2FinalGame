class DebugCollector:
    """сборщик отладочных данных. Устанвока переменных"""
    
    def __init__(self):
        self._data = {}
    
    def set(self, key: str, value: any) -> None:
        """устанавливает значение переменной. Дроби округляет до 3 знаков"""
        # round first
        round_digits = 3
        if isinstance(value, float):
            value = round(value, round_digits)
        elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            value = [round(v, round_digits) if isinstance(v, float) else v for v in value]
        
        self._data[key] = value
    
    def get(self, key: str, default=None) -> any:
        """возвращает значение переменной. Если переменная не установлена, возвращает default"""
        return self._data.get(key, default)

    def increase(self, key: str, value: int) -> None:
        """увеличивает значение переменной на value. Если переменная не установлена, ставится на value"""
        self.set(key, self.get(key, 0) + value)
    
    def get_all(self) -> dict:
        """возвращает все переменные"""
        return self._data.copy()
    
    def clear(self) -> None:
        """очищает все переменные"""
        self._data.clear()
