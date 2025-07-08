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
            raise ValueError("識別子は1〜255の範囲でなければなりません。")
        if identifier in DataManager._instances:
            raise ValueError(f"識別子 {identifier} はすでに使用されています。")
        if length <= 0:
            raise ValueError("データの長さは1以上でなければなりません。")
        if not isinstance(data_type, DataType):
            raise ValueError("data_typeはDataType Enumでなければなりません。")
        self._identifier:int = identifier
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
        try:
            packed_data = struct.pack(self._pack_mode, *self._data)
        except struct.error as e:
            raise ValueError(f"データのパックに失敗しました: {e}")
        return packed_data
    
    def identifier(self):
        """識別子を取得する
        :return: 1byteの識別子 (1〜255)
        """
        return self._identifier

    # def _data_check(self):
    #     """データの型と長さをチェックする
    #     :raises ValueError: データの型や長さが不正な場合
    #     """
    #     if len(self._data) != struct.calcsize(self._pack_mode):
    #         raise ValueError(f"データの長さが不正です。期待される長さ: {struct.calcsize(self._pack_mode)}, 実際の長さ: {len(self._data)}")
    #     try:
    #         struct.pack(self._pack_mode, *self._data)
    #     except struct.error as e:
    #         raise ValueError(f"データの型が不正です: {e}")

    @classmethod
    def _search(cls, identifier:int):
        """指定された識別子のDataManagerインスタンスを検索する
        :param identifier: 1byteの識別子 (1〜255)
        :return: DataManagerインスタンス
        :raises ValueError: 指定された識別子のインスタンスが存在し
        """
        if identifier not in cls._instances:
            raise ValueError(f"識別子 {identifier} のDataManagerインスタンスが存在しません。")
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

