from scoreSectionDesigns.decorations import check_decorations, decorations
from scoreSectionDesigns.notes import check_notes, notes
from tests.common import GraphicUnitTest

check_notes()
check_decorations()


class DesignRenderingTestCases(GraphicUnitTest):
    pass


for nid in notes:
    note = notes[nid]
    name = note.name.lower()
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    setattr(DesignRenderingTestCases, f"test_{name}",
            lambda self: DesignRenderingTestCases.scatter_render(self, notes[nid].make_canvas(), *notes[nid].size))

for did in decorations:
    decoration = decorations[did]
    name = decoration.name.lower()
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    setattr(DesignRenderingTestCases, f"test_{name}",
            lambda self: DesignRenderingTestCases.scatter_render(self, decorations[did].make_canvas(head_height=10,
                                                                                                    height=10),
                                                                 decorations[did].width, decorations[did].min_height))


__all__ = ["DesignRenderingTestCases"]
