from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from llvm_declarations import LlvmName, LlvmType, TypeDeclaration
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
    data_type: Optional[TypeDeclaration] = None
    driver: Optional[str] = None
    source: Optional[LlvmName] = None
    def get_driver(self) -> Optional[Union[LlvmType, str]]:
        if self.driver is None:
            return self.source
        return self.driver

class SourceNotFound(Exception):
    pass

class AssignmentResolution:

    _assignment_map : Dict[LlvmName, AssignmentItem] = {}

    def __init__(self):
        self._msg = Messages()

    def _append_source(self, name: LlvmName, sources: List[AssignmentItem]) -> Optional[LlvmName]:
        self._msg.function_start("name=" + str(name) + ", sources=" + str(sources))
        found_source = self._assignment_map[name]
        sources.append(found_source)
        result = found_source.source
        self._msg.function_end(result)
        return result

    def get_source(self, search_source: LlvmName) -> List[AssignmentItem]:
        self._msg.function_start("search_source=" + str(search_source))
        result: List[AssignmentItem] = []
        name: Optional[LlvmName] = search_source
        while (name is not None) and (name in self._assignment_map):
            name = self._append_source(name=name, sources=result)
        self._msg.function_end(result)
        return result

    def add_assignment(self, destination: LlvmName, assignment: AssignmentItem):
        self._msg.function_start("destination=" + str(destination) +
        ", assignment=" + str(assignment))
        self._assignment_map[destination] = assignment
        self._msg.function_end()
