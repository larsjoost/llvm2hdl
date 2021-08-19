class FileWriter:

    def __init__(self, file_handle):
        self.file_handle = file_handle

    def write(self, text):
        self.file_handle.write(text)

    def writeln(self, text):
        self.write(text)
        self.write("\n")