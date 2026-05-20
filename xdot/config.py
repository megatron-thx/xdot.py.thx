#
# megatron-thx multiline patch Tbilisi 2026
#

from dataclasses import dataclass

@dataclass
class Config:
    multi_line_activate: bool
    line_separator: str
    dark_theme: bool
    y_correction_factor: float

config = Config(
    multi_line_activate = False,
    line_separator = ";",
    dark_theme = False,
    y_correction_factor = 7.232
)

print(config)