from dataclasses import dataclass
from typing import Dict

from llvm_declarations import LlvmName, TypeDeclaration
from messages import Messages

@dataclass
class AssignmentItem:
    """
    AssignmentItem contains all elements needed to resolve the original signal driver
    Examples:
    "%0 = load i32, i32* %a, align 4, !tbaa !2"
    AssignmentItem(destination="%0", source="%a", data_type=TypeDeclaration("i32*"), endpoint=False)
    %add.1 = add nsw i32 %1, %0
    AssignmentItem(destination="%add.1", source=<output port of add>, data_type=TypeDeclaration("i32"), endpoint=True)
    """
    destination: LlvmName
    source: LlvmName
    data_type: TypeDeclaration
    endpoint : bool

class SourceNotFound(Exception):
    pass

class AssignmentResolution:

    _assignment_map : Dict[LlvmName, AssignmentItem] = {}

    def __init__(self):
        self._msg = Messages()

    def get_source(self, assignment: AssignmentItem) -> AssignmentItem:
        self._msg.function_start("get_source(assignment=" + str(assignment) + ")")
        if assignment.endpoint or assignment.source not in self._assignment_map:
            result = assignment
        else:
            result = self.get_source(self._assignment_map[assignment.source])
        self._msg.function_end("get_source = " + str(result))
        return result

    def add_assignment(self, assignment: AssignmentItem):
        self._assignment_map[assignment.destination] = assignment
