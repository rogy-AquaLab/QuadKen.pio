import struct

class DataManager:
    def __init__(self, data_type:int, length:int, pack_mode:str):
        if 1 <= data_type <= 255:
            raise ValueError("1byte only")
        if len(pack_mode) != length:
            raise ValueError("Invalid pack mode. Length of pack mode must match the numbe")

        self._data_type:int = data_type
        self._data = [0] * length  # uint8_t 8個のデータを格納するリスト
        self._length = length
        self._pack_mode = pack_mode

    def __str__(self):
        return f"データ{self._data_type} : {self._data})"
    


    def data_type(self):
        return self._data_type
    
    def update_data(self, new_data):
        self._data = new_data[:]

    def unpack(self, byte_data):
        if len(byte_data) != self._length:
            raise ValueError("Invalid byte data length. Length of byte data must match th")
        self._data = list(struct.unpack(self._pack_mode, byte_data))
        return self._data

    def get_data(self):
        return self._data

    def pack_data(self):
        # uint8_t 8個のデータを送る（例: 0〜7）
        return struct.pack(self._pack_mode, *self._data)
