class VhdlDeclarations:

    def getTypeDeclarations(self, data_width):
        return "std_ulogic" if data_width == 1 else "std_ulogic_vector(0 to " + str(data_width) + " - 1)"
		