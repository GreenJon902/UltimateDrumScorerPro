from gl.instructions.instruction import Instruction


class ArgInstruction(Instruction):
    def __init__(self, function: callable):
        self.run = function
