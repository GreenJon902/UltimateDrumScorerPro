class MetricConverterClass:
    def to_mm(self, length: float) -> float:
        raise NotImplementedError(f"To mm for {self.__class__.__name__} is not implemented")

    def to_pt(self, length: float) -> float:
        raise NotImplementedError(f"To mm for {self.__class__.__name__} is not implemented")

    def to_px(self, length: float) -> float:
        raise NotImplementedError(f"To mm for {self.__class__.__name__} is not implemented")









px_per_mm = 20
pt_per_mm = 2.835


page_size_mm = 210, 297
page_size_px = page_size_mm[0] * px_per_mm, page_size_mm[1] * px_per_mm


# noinspection PyMethodMayBeStatic
class _Page:
    def width_to_height(self, px: float) -> float:
        return px * (page_size_px[1] / page_size_px[0])

    def height_to_width(self, px: float) -> float:
        return px * (page_size_px[0] / page_size_px[1])


class _MM(MetricConverterClass):
    def to_mm(self, mm: float) -> float:
        return mm

    def to_pt(self, mm: float) -> float:
        return mm * pt_per_mm

    def to_px(self, mm: float) -> float:
        return mm * px_per_mm


class _PT(MetricConverterClass):
    def to_mm(self, pt: float) -> float:
        return pt / pt_per_mm

    def to_pt(self, pt: float) -> float:
        return pt

    def to_px(self, pt: float) -> float:
        return MM.to_px(self.to_mm(pt))


class _PX(MetricConverterClass):
    def to_mm(self, px: float) -> float:
        return px / px_per_mm

    def to_pt(self, px: float) -> float:
        return MM.to_pt(self.to_mm(px))

    def to_px(self, px: float) -> float:
        return px



MM = _MM()
PT = _PT()
PX = _PX()

Page = _Page()

