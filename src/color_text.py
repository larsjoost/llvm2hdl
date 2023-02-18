"""
Adds color codes to text
"""
from typing import Any, List, Optional, Union


class ColorText:
    """
    Adds color codes to text
    """

    def __init__(self, text, color=None) -> None:
        colors = {
            "magenta": '\033[95m',
            "blue": '\033[94m',
            "yellow": '\033[93m',
            "green": '\033[92m',
            "red": '\033[91m'}
        self.color_lut = {
            "header": colors["magenta"],
            "warning": colors["yellow"],
            "note": colors["blue"],
            "ok": colors["green"],
            "error": colors["red"],
            "fail": colors["red"],
            "failure": colors["red"],
            "endc": '\033[0m',
            "foreground": '\033[0m',
            "bold": '\033[1m',
            "underline": '\033[4m',
        } | colors
        self.text = text
        self.color = color

    def add_color(self, text: str) -> str:
        color = self.color
        if color is None:
            return text
        if not isinstance(color, list):
            color = [color]
        translated_colors = [self.color_lut[i] for i in color]
        return "".join(translated_colors) + text + self.color_lut["endc"]

    def get_text(self):
        return self.add_color(self.text)

    def center(self, size):
        return self.add_color(self.text.center(size))

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.get_text()

    def __repr__(self):
        return self.get_text()

class HighLight:

    def highlight_replace(self, text: Any, highlight: Optional[Union[List[str], str]], color="red") -> str:
        if highlight is None:
            return str(text)
        if not isinstance(highlight, list):
            highlight = [highlight]
        highlighted_text = str(text)
        for i in highlight:
            highlight_replace = str(ColorText(text=i, color=color))
            highlighted_text = highlighted_text.replace(i, highlight_replace)
        return highlighted_text
