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
    """データ管理クラス
    1byteの識別子を持ち、指定された長さとデータ型でデータを管理する。
    データをはコンストラクタで指定して、パックとアンパックが可能。
    """
    _instances = {}

    def __init__(self, identifier:int, length:int, data_type:DataType):
        """コンストラクタ
        :param identifier: 1byteの識別子 (1〜255)
        :param length: データの長さ
        :param data_type: データの型 (DataType Enum)
        """
        if not 1 <= identifier <= 255:
            raise ValueError("1byte only")

        self._data_type:int = data_type
        self._data = [0] * length  # uint8_t 8個のデータを格納するリスト
        self._pack_mode = data_type.value * length
        DataManager._instances[identifier] = self

    def __repr__(self):
        return f"データ{self._data_type} : {self._data})"
    
    def update(self, new_data):
        """データを更新する
        :param new_data: 更新するデータのリスト
        """
        self._data = new_data[:]

    def get(self):
        """現在のデータを取得する
        :return: 現在のデータのリスト
        """
        return self._data

    def pack(self):
        """データをパックしてバイト列に変換する
        :return: パックされたバイト列
        """
        # uint8_t 8個のデータを送る（例: 0〜7）
        return struct.pack(self._pack_mode, *self._data)
    
    def identifier(self):
        """識別子を取得する
        :return: 1byteの識別子 (1〜255)
        """
        return next((k for k, v in DataManager._instances.items() if v is self), None)  

    @classmethod
    def _search(cls, identifier:int):
        """指定された識別子のDataManagerインスタンスを検索する
        :param identifier: 1byteの識別子 (1〜255)
        :return: DataManagerインスタンス
        :raises ValueError: 指定された識別子のインスタンスが存在し
        """
        if not 1 <= identifier <= 255:
            raise ValueError("1byte only")
        if identifier not in cls._instances:
            raise ValueError(f"DataManager with identifier {identifier} does not exist.")
        instance = cls._instances[identifier]
        return instance
    
    @classmethod
    def unpack(cls, identifier:int, data:bytes):
        """指定された識別子のDataManagerインスタンスを検索し、データをアンパックする
        :param identifier: 1byteの識別子 (1〜255)
        :param data: アンパックするバイト列
        :return: アンパックされたデータのリスト
        :raises ValueError: 指定された識別子のインスタンスが存在しない場合
        """
        instance = cls._search(identifier)
        instance._data = list(struct.unpack(instance._pack_mode, data))
        return instance._data

