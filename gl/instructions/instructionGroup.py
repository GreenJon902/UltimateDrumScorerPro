from gl.instructions.instruction import Instruction


class InstructionGroup(Instruction):
    _instructions: list[Instruction]

    def __init__(self):
        self._instructions = list()

    def run(self):
        for instruction in self._instructions:
            instruction.run()

    def add(self, instruction: Instruction):
        self._instructions.append(instruction)
