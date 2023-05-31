from kivy.graphics import InstructionGroup


class ScoreSection_ComponentOrganiserBase:
    group: InstructionGroup

    def add_section(self, index, head_info=None, bar_info=None, dot_info=None, stem_info=None) -> \
            list[tuple[tuple[any, ...], dict[str, any]]]:
        raise NotImplementedError()

    def setup(self, group: InstructionGroup):
        """
        Resets and setups the group for use in this component organiser type, this could be clearing it or adding
        certain transforms.
        """
        self.group = group
        group.clear()


__all__ = ["ScoreSection_ComponentOrganiserBase"]
