class RestConfig:
    compactIntoWholeRest = True
    compactIntoHalfRest = True


class TimeSignatureConfig:
    fontSize = 15
    color = (0, 0, 0, 1)

    drawTimeSignatureOnChange = True
    alwaysDrawTimeSignature = False  # Overpowers BarConfig.drawTimeSignatureOnChange when true


class BarConfig:
    pass



class NotationRendererConfig:
    restConfig: RestConfig = RestConfig()
    barConfig: BarConfig = BarConfig()
    timeSignatureConfig: TimeSignatureConfig = TimeSignatureConfig()



__all__ = ["NotationRendererConfig"]
