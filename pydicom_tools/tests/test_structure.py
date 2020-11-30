import os
from .. import RTSS

BASE = os.path.abspath(os.path.dirname(__file__))
SAMPLE_DIR = os.path.join(BASE, '..', 'sample')
RTSS_NAME = "RS.002445.dcm"


class TestStructure:
    """
    Structureモジュールのテスト
    """

    def test_init(self):
        rtss = RTSS(os.path.join(SAMPLE_DIR, RTSS_NAME))

        assert rtss.structures[1] == 'RT LENS'
