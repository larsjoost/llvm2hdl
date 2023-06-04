
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Token(ABC):
    content: str = ""
    @abstractmethod
    def abort(self, letter: str) -> bool:
        pass
    @abstractmethod
    def absorb_abort_letter(self, letter: str) -> Optional[str]:
        pass
    @abstractmethod
    def is_bracket_token(self) -> bool:
        pass
    @abstractmethod
    def contains_comma(self) -> bool:
        pass
    def is_empty(self) -> bool:
        return len(self.content.strip()) == 0
    @abstractmethod
    def get_content(self) -> str:
        pass
    def remove_everything_after_comma(self) -> Optional[str]:
        comma_split = self.content.split(",", maxsplit=1)
        first_part = comma_split[0].strip()
        return None if len(first_part) == 0 else first_part
    @abstractmethod
    def is_split_allowed(self) -> bool:
        pass
    def split(self, delimiter: str) -> List[str]:
        return self.content.split(delimiter)
    
class BracketToken(Token):
    def abort(self, letter: str) -> bool:
        return letter == "]"
    def absorb_abort_letter(self, letter: str) -> None:
        self.content += letter
        return None
    def is_bracket_token(self) -> bool:
        return True
    def contains_comma(self) -> bool:
        return False
    def get_content(self) -> str:
        return self.content.replace("[", "").replace("]", "")
    def is_split_allowed(self) -> bool:
        return False

class TextToken(Token):
    def abort(self, letter: str) -> bool:
        return letter == "["
    def absorb_abort_letter(self, letter: str) -> Optional[str]:
        return letter
    def is_bracket_token(self) -> bool:
        return False
    def contains_comma(self) -> bool:
        return "," in self.content
    def get_content(self) -> str:
        return self.content
    def is_split_allowed(self) -> bool:
        return True

class TokenFactory():
    def create(self, letter: str) -> Token:
        return BracketToken() if letter == '[' else TextToken()
        
class BracketTokenizer:

    def _abort(self, result: List[Token], token: Token, letter: str) -> Token:
        abort_letter = token.absorb_abort_letter(letter=letter)
        result.append(token)
        token = TokenFactory().create(letter=letter)
        if abort_letter is not None:
            token.content = abort_letter
        return token

    def _new(self, letter: str) -> Token:
        token = TokenFactory().create(letter=letter)
        token.content = letter
        return token

    def tokenize(self, line: str) -> List[Token]:
        result: List[Token] = []
        token: Optional[Token] = None
        for letter in line:
            if token is None:
                token = self._new(letter=letter)
            elif token.abort(letter=letter):
                token = self._abort(result=result, token=token, letter=letter)
            else:
                token.content += letter
        if token is not None:
            result.append(token)
        return result
