from __future__ import annotations

import json
import typing

if typing.TYPE_CHECKING:
    from scoreSectionDesigns import Design


def read_design_from(path: str, type_: type(Design)) -> tuple[int, Design]:
    print(f"Reading design from {path}...")

    with open(path, 'r') as f:
        serialized = json.load(f)

    json_instructions = serialized.pop("instructions")
    instructions = []  # Factory.get(instr.pop("name"))(**instr) for instr in json_instructions
    for instr in json_instructions:
        name = instr.pop("name")
        instructions.append(name + "(" + ", ".join(attr + "=" + repr(value) for attr, value in instr.items()) + ")")

    nid = serialized.pop("id")
    attributes = serialized
    design = type_(instructions, **attributes)

    print(f"Finished, read {design}")
    return nid, design


__all__ = ["read_design_from"]