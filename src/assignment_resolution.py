from dataclasses import dataclass
from typing import Dict, Optional

from llvm_declarations import LlvmName, TypeDeclaration
from messages import Messages

@dataclass
class AssignmentItem:
    """
    AssignmentItem contains all elements needed to resolve the original signal driver
    Examples:
    "load i32, i32* %a, align 4, !tbaa !2"
    AssignmentItem(source="%a", data_type=TypeDeclaration("i32*"))
    "add nsw i32 %1, %0"
    AssignmentItem(driver=<output port of add>, data_type=TypeDeclaration("i32"))
    """
    data_type: TypeDeclaration
    driver: Optional[str] = None
    source: Optional[LlvmName] = None
    def get_driver(self) -> str:
        if self.driver is None:
            return self.source.get_variable_name()
        return self.driver

class SourceNotFound(Exception):
    pass

class AssignmentResolution:

    _assignment_map : Dict[LlvmName, AssignmentItem] = {}

    def __init__(self):
        self._msg = Messages()

    def get_source(self, assignment: AssignmentItem) -> AssignmentItem:
        self._msg.function_start("get_source(assignment=" + str(assignment) + ")")
        result = assignment
        if assignment.source is not None:
            assignment_search = assignment.source
            if assignment_search in self._assignment_map:
                result = self.get_source(self._assignment_map[assignment_search])
        self._msg.function_end("get_source = " + str(result))
        return result

    def add_assignment(self, destination: LlvmName, assignment: AssignmentItem):
        self._msg.function_start("add_assignment(destination=" + str(destination) +
        ", assignment=" + str(assignment) + ")")
        self._assignment_map[destination] = assignment
        self._msg.function_end("add_assignment")
