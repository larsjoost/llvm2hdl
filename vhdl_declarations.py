from typing import Union

class VhdlDeclarations:

    def get_type_declarations(self, data_width: Union[int, str]) -> str:
        if data_width == 1:
            return "std_ulogic"
        return "std_ulogic_vector(0 to " + str(data_width) + " - 1)"
		