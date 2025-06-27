import struct
from enum import Enum

class DataType(Enum):
    UINT8 = "B"
    UINT16 = "H"
    UINT32 = "I"
    INT8 = "b"
    INT16 = "h"
    INT32 = "i"

class DataManager:



    _instances = {}

    def __init__(self, identifier:int, length:int, data_type:DataType):
        if not 1 <= identifier <= 255:
            raise ValueError("1byte only")

        self._data_type:int = data_type
        self._data = [0] * length  # uint8_t 8個のデータを格納するリスト
        self._pack_mode = data_type.value * length
        DataManager._instances[identifier] = self

    def __repr__(self):
        return f"データ{self._data_type} : {self._data})"
    
    def update(self, new_data):
        self._data = new_data[:]

    def get(self):
        return self._data

    def pack(self):
        # uint8_t 8個のデータを送る（例: 0〜7）
        return struct.pack(self._pack_mode, *self._data)

    @classmethod
    def _search(cls, identifier:int):
        if not 1 <= identifier <= 255:
            raise ValueError("1byte only")
        if identifier not in cls._instances:
            raise ValueError(f"DataManager with identifier {identifier} does not exist.")
        instance = cls._instances[identifier]
        return instance
    
    @classmethod
    def unpack(cls, identifier:int, data:bytes):
        instance = cls._search(identifier)
        instance._data = list(struct.unpack(instance._pack_mode, data))
        return instance._data

