from scoreSectionDesigns.notes import check_notes, notes
from tests.common import GraphicUnitTest

check_notes()


class DesignRenderingTestCases(GraphicUnitTest):
    pass


for nid in notes:
    note = notes[nid]
    name = note.name.lower()
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    setattr(DesignRenderingTestCases, f"test_{name}",
            lambda self: DesignRenderingTestCases.scatter_render(self, notes[nid].make_canvas(), *notes[nid].size))


__all__ = ["DesignRenderingTestCases"]
