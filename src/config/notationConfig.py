class BufferSpace:
    before = 0
    after = 0

    def __init__(self, before=0, after=0):
        self.before = before
        self.after = after


class RestConfig:
    quarterRestHeight = 50

    bufferSpace: BufferSpace = BufferSpace(after=5)


class TimeSignatureConfig:
    fontSize = 15
    color = (0, 0, 0, 1)

    drawTimeSignatureOnChange = True
    alwaysDrawTimeSignature = False  # Overpowers BarConfig.drawTimeSignatureOnChange when true

    bufferSpace: BufferSpace = BufferSpace(after=10)


class BarConfig:
    pass



class NotationRendererConfig:
    restConfig: RestConfig = RestConfig()
    barConfig: BarConfig = BarConfig()
    timeSignatureConfig: TimeSignatureConfig = TimeSignatureConfig()



__all__ = ["NotationRendererConfig"]
