
from dataclasses import dataclass
from typing import Callable, List, Optional

@dataclass
class LlvmSourceLine:
    line_number: int
    line : str
    
    def is_comment(self) -> bool:
        return self.line.startswith(";")
    def is_constant(self) -> bool:
        return self.line.startswith(("@", "%"))
    def is_function_start(self) -> bool:
        return self.line.strip().startswith("define ")
    def is_function_end(self) -> bool:
        return self.line.strip().endswith("}")
    def is_label(self) -> bool:
        return ":" in self.line
    def is_assignment(self) -> bool:
        return "=" in self.line
    def get_elaborated(self) -> str:
        return f"Line {self.line_number}: {self.line}"

@dataclass
class LlvmSourceFile:    
    lines: List[LlvmSourceLine]

@dataclass
class LlvmSourceConstants:
    lines: List[LlvmSourceLine]

@dataclass
class LlvmSourceFunction:
    lines: List[LlvmSourceLine]

@dataclass
class LlvmSourceFunctions:
    functions: List[LlvmSourceFunction]

class LlvmSourceFileParser:

    def _remove_comments(self, lines: List[LlvmSourceLine]) -> List[LlvmSourceLine]:
        return [line for line in lines if not line.is_comment()]

    def _extract_lines(self, lines: List[str]) -> List[LlvmSourceLine]:
        return [LlvmSourceLine(line_number=line_number, line=line) for line_number, line in enumerate(lines, 1)]

    def load(self, lines: List[str]) -> LlvmSourceFile:
        source_lines = self._extract_lines(lines=lines)
        return LlvmSourceFile(self._remove_comments(lines=source_lines))

    def extract_constants(self, source_file: LlvmSourceFile) -> LlvmSourceConstants:
        constant_lines = [line for line in source_file.lines if line.is_constant()]
        return LlvmSourceConstants(lines=constant_lines)

    def _index(self, lines: List[LlvmSourceLine], end_condition: Callable) -> Optional[int]:
        return next(
            (
                index
                for index, line in enumerate(lines, 1)
                if end_condition(line)
            ),
            None,
        )

    def _index_function_start(self, lines: List[LlvmSourceLine]) -> Optional[int]:
        def end_condition(x):
            return x.is_function_start()
        return self._index(lines=lines, end_condition=end_condition)

    def _index_function_end(self, lines: List[LlvmSourceLine]) -> Optional[int]:
        def end_condition(x):
            return x.is_function_end()
        return self._index(lines=lines, end_condition=end_condition)

    @dataclass
    class FunctionLineLocation:
        start: int
        end: int
        def extract_function(self, lines: List[LlvmSourceLine]) -> List[LlvmSourceLine]:
            return lines[self.start-1:self.end]
        def extract_rest(self, lines: List[LlvmSourceLine]) -> List[LlvmSourceLine]:
            return lines[self.end:]

    def _find_function_location(self, lines: List[LlvmSourceLine]) -> Optional[FunctionLineLocation]:
        start_index = self._index_function_start(lines=lines)
        if start_index is None:
            return None
        lines = lines[start_index:]
        end_index = self._index_function_end(lines=lines)
        assert end_index is not None, f"Could not find end of function start {lines[start_index]}"
        return self.FunctionLineLocation(start=start_index, end=end_index+start_index)

    def _extract_function(self, lines: List[LlvmSourceLine], source_functions: List[LlvmSourceFunction]) -> None:
        location = self._find_function_location(lines=lines)
        if location is None:
            return
        function_lines = location.extract_function(lines=lines)
        source_functions.append(LlvmSourceFunction(lines=function_lines))
        rest_lines = location.extract_rest(lines=lines)
        self._extract_function(lines=rest_lines, source_functions=source_functions)

    def extract_functions(self, source_file: LlvmSourceFile) -> LlvmSourceFunctions:
        lines = source_file.lines
        source_functions: List[LlvmSourceFunction] = []
        self._extract_function(lines=lines, source_functions=source_functions)
        return LlvmSourceFunctions(functions=source_functions)
