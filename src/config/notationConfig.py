class BufferSpace:
    before = 0
    after = 0

    def __init__(self, before=0, after=0):
        self.before = before
        self.after = after


class RestConfig:
    quarterRestHeight = 50

    bufferSpace: BufferSpace = BufferSpace(after=20)


class TimeSignatureConfig:
    fontSize = 15
    color = (0, 0, 0, 1)

    drawTimeSignatureOnChange = True
    alwaysDrawTimeSignature = False  # Overpowers BarConfig.drawTimeSignatureOnChange when true

    bufferSpace: BufferSpace = BufferSpace(after=10)


class BarConfig:
    staffSpacing = 10


class RoundNoteHeadConfig:
    color = (0, 0, 0, 1)
    width = 15
    height = 10


class NoteHeadConfig:
    roundNoteHead: RoundNoteHeadConfig = RoundNoteHeadConfig()
    round_heads = ["kick", "snare"]
    noteHeadLevel = {"kick": 1, "snare": 3}


class BeatConfig:
    bufferSpace: BufferSpace = BufferSpace(after=10)


class NotationRendererConfig:
    restConfig: RestConfig = RestConfig()
    barConfig: BarConfig = BarConfig()
    timeSignatureConfig: TimeSignatureConfig = TimeSignatureConfig()
    noteHeadConfig: NoteHeadConfig = NoteHeadConfig()
    beatConfig: BeatConfig = BeatConfig()



__all__ = ["NotationRendererConfig"]
