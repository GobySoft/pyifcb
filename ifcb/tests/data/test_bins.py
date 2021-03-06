import unittest
import os
import shutil

from ifcb.tests.utils import test_dir

from ifcb.data.io import open_raw
from ifcb.data.bins import BaseBin
from ifcb.data.identifiers import Pid
from ifcb.data.adc import SCHEMA

from .fileset_info import list_test_bins
from .bins import assert_bin_equals

class MockBin(BaseBin):
    def __init__(self, pid):
        self.pid = Pid(pid)

class TestBaseBin(unittest.TestCase):
    def test_v1_schema_attrs(self):
        b = MockBin('IFCB1_2000_001_000000')
        assert b.schema == SCHEMA[1]
    def test_v2_schema_attrs(self):
        b = MockBin('D20000101T000000_IFCB001')
        assert b.schema == SCHEMA[2]

class TestMemoryBin(unittest.TestCase):
    def test_read_cmgr(self):
        for a in list_test_bins():
            with a:
                b = a.read()
            assert_bin_equals(a, b)
    def test_read(self):
        for a in list_test_bins():
            b = a.read()
            assert_bin_equals(a, b)
    def test_read_del(self):
        for a in list_test_bins():
            with test_dir() as d:
                shutil.copy(a.fileset.adc_path, d)
                shutil.copy(a.fileset.roi_path, d)
                shutil.copy(a.fileset.hdr_path, d)
                p = os.path.join(d, os.path.basename(a.fileset.adc_path))
                with open_raw(p) as b:
                    c = b.read()
            assert_bin_equals(a, c)
