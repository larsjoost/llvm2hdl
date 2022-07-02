"""
Adds color codes to text
"""
class ColorText:
    """
    Adds color codes to text
    """

    def __init__(self, text, color=None):
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
            "underline": '\033[4m'}
        self.color_lut.update(colors)
        self.text = text
        self.color = color

    def add_color(self, text: str) -> str:
        color = self.color
        if color is not None:
            if not isinstance(color, list):
                color = [color]
            translated_colors = [self.color_lut[i] for i in color]
            result = "".join(translated_colors) + text + self.color_lut["endc"]
        else:
            result = text
        return result

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
