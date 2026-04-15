#
# megatron-thx multiline patch Tbilisi 2026
#

from dataclasses import dataclass

@dataclass
class Config:
    multi_line_activate: bool
    line_separator: str

config = Config(
    multi_line_activate= False,
    line_separator= ";"
)

print(config)