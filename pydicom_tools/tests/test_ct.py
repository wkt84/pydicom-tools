import os
from .. import CTImage

BASE = os.path.abspath(os.path.dirname(__file__))
SAMPLE_DIR = os.path.join(BASE, '..', 'sample')


class TestCT:
    """
    CTモジュールのテスト
    """

    def test_init(self):
        ct = CTImage()
        assert ct.is_loaded is False

    def test_load(self):
        ct = CTImage()
        ct.load(SAMPLE_DIR)

        assert ct.is_loaded is True
        assert ct.volume.shape == (5, 512, 512)
