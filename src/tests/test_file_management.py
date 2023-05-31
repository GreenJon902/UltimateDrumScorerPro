import os
import unittest

from parameterized import parameterized

from kv import check_kv
from scoreSectionDesigns import notes, read_design_from
from scoreSectionDesigns.notes import Note


class FileManagementTestCases(unittest.TestCase):
    @parameterized.expand(os.listdir(notes.path))
    def test_load_default_note(self, name):
        read_design_from(os.path.join(notes.path, name), Note)

    def test_loading_all_kv(self):
        check_kv(force=True)
