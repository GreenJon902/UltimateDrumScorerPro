class Text_FormatterBase:
    def format(self, text) -> str:
        raise NotImplementedError()


__all__ = ["Text_FormatterBase"]
