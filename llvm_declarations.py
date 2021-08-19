
class LlvmDeclarations:

    def getDataWidth(self, data_type : str):
        data_types = {'i32': 32}
        return data_types[data_type]
