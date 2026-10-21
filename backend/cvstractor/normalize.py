import re
from dataclasses import dataclass

from .patterns import NOISE

@dataclass
class Line:
    text: str
    position: int

def normalize_lines(raw_lines):
    result = []
    previous = None
    for raw in raw_lines:
        text = str(raw).replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
        text = text.replace("—", "-").replace("–", "-").replace("−", "-")
        for part in text.split("\n"):
            clean = re.sub(r"\s+", " ", part).strip()
            if not clean or NOISE.fullmatch(clean) or clean == previous:
                continue
            result.append(Line(clean, len(result) + 1))
            previous = clean
    return result
