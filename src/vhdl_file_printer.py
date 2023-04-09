
import os
from typing import List

from vhdl_function_contents import VhdlFunctionContents


class VhdlFilePrinter:

    def generate(self, file_name: str, contents: List[VhdlFunctionContents]) -> None:
        with open(file_name, 'w', encoding="utf-8") as file_handle:
            for i in contents:
                print(i.get_contents(), file=file_handle, end="")
        base_name = os.path.splitext(file_name)[0]
        instance_file_name = f'{base_name}.inc'
        with open(instance_file_name, 'w', encoding="utf-8") as file_handle:
            for i in contents:
                print(i.get_instances(), file=file_handle)
