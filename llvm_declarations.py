
class LlvmDeclarations:

    def get_data_width(self, data_type: str) -> int:
        if data_type[0] == "i":
            return int(data_type[1:])
        data_types = {'i32': 32, 'float': 32}
        return data_types[data_type]
