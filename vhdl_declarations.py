from typing import Union

class VhdlDeclarations:

    _data_width: Union[int, str]

    def __init__(self, data_width: Union[int, str]):
        self._data_width = data_width

    def get_data_width(self) -> str:
        return str(self._data_width)

    def get_type_declarations(self) -> str:
        return "std_ulogic_vector(0 to " + str(self._data_width) + " - 1)"
		