from kivy.graphics import InstructionGroup

from renderer.scoreSection import SectionSectionInfoHolder


class ScoreSection_ComponentOrganiserBase:
    group: InstructionGroup

    def setup(self, group: InstructionGroup):
        """
        Resets and setups the group for use in this component organiser type, this could be clearing it or adding
        certain transforms.
        """
        pass

    def build(self, head_group=None, bar_group=None, dot_group=None) -> InstructionGroup:
        """
        Takes the arguments and lays them out ready to be organised
        """
        raise NotImplementedError()

    def parent_insert(self, group: InstructionGroup, index: int, built_group: InstructionGroup):
        """
        Insert a built group into the parents canvas
        """
        raise NotImplementedError()

    def organise(self, ssihs: list[SectionSectionInfoHolder], head_height: float) \
            -> tuple[float, float]:
        """
        Organises each item in ssihs with the given information, returns the width and height.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_ComponentOrganiserBase"]
