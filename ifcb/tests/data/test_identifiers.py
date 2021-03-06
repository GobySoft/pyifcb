import unittest
import random

from ifcb.data import identifiers as ids
from ifcb.data.identifiers import Pid

"""
ways to mess up an identifier:

* insert any character anywhere
* delete any character anywhere
* change any letter to a letter other than 'D', 'T', 'I', 'F', 'C', or 'B'
* add two extensions, products, or targets

"""

GOOD_V1 = 'IFCB1_2000_001_123456'
GOOD_V2 = 'D20000101T123456_IFCB001'

GOOD = [GOOD_V1, GOOD_V2]

ALPHA = 'IFCBDTXYZ'
CHARS = '0123456789_' + ALPHA

class DestroyPid(object):
    def __init__(self, pid):
        self.pid = pid
    def insert_character(self):
        for d in CHARS:
            for i in range(len(self.pid)+1):
                yield self.pid[:i] + d + self.pid[i:]
    def delete_character(self):
        for i in range(len(self.pid)):
            yield self.pid[:i] + self.pid[i+1:]
    def mod_letter(self):
        for i in range(len(self.pid)):
            pc = self.pid[i]
            if pc not in ALPHA:
                continue
            for c in ALPHA:
                if c == pc: continue
                yield self.pid[:i] + c + self.pid[i+1:]
                
# FIXME test cmp
class TestIdentifiers(unittest.TestCase):
    def test_schema_version(self):
        assert Pid(GOOD_V1).schema_version == 1, 'expected schema version 1'
        assert Pid(GOOD_V2).schema_version == 2, 'expected schema version 2'
    def test_unparse(self):
        for pid in GOOD:
            assert ids.unparse(Pid(pid).parsed) == pid
    def test_timestamp(self):
        for pid in GOOD:
            dt = Pid(pid).timestamp
            assert dt.year == 2000, 'year wrong'
            assert dt.month == 1, 'month wrong'
            assert dt.day == 1, 'day wrong'
            assert dt.hour == 12, 'hour wrong'
            assert dt.minute == 34, 'minute wrong'
            assert dt.second == 56, 'second wrong'
    def test_target(self):
        target = 123
        target_string = '%05d' % target
        for pid in GOOD:
            target_pid = '%s_%s' % (pid, target_string)
            assert Pid(target_pid).target == target, 'target wrong'
    def test_destroy(self):
        for pid in GOOD:
            d = DestroyPid(pid)
            for p in d.insert_character():
                with self.assertRaises(ValueError):
                    Pid(p).parsed
            for p in d.delete_character():
                with self.assertRaises(ValueError):
                    Pid(p).parsed
            for p in d.mod_letter():
                with self.assertRaises(ValueError):
                    Pid(p).parsed
    def test_pathname(self):
        path_prefixes = ['\\foo\\bar\\', 'C:\\foo\\bar\\', '/foo/bar/']
        for pid in GOOD:
            for pp in path_prefixes:
                Pid(pp + pid).parsed
    @unittest.skip('failing')
    def test_two_extensions(self):
        for spid in GOOD:
            with self.assertRaises(ValueError):
                # does not fail, returns extension 'foo'
                Pid(spid + '.foo.bar').parsed
    @unittest.skip('failing')
    def test_two_products(self):
        for spid in GOOD:
            with self.assertRaises(ValueError):
                # does not fail, returns product 'foo_bar'
                Pid(spid + '_foo_bar').parsed
    @unittest.skip('failing')
    def test_two_targets(self):
        for spid in GOOD:
            with self.assertRaises(ValueError):
                # does not fail, returns target '00001'
                Pid(spid + '_00001_00007').parsed
    def test_target(self):
        for spid in GOOD:
            target = 27
            pid = Pid('%s_%05d' % (spid, target))
            assert pid.target == target
    def test_with_target(self):
        for spid in GOOD:
            pid = Pid(spid)
            target = 27
            expected = spid + '_%05d' % 27
            assert pid.with_target(target) == expected
    def test_product(self):
        for spid in GOOD:
            product = 'foo'
            pid = Pid('%s_%s' % (spid, product))
            assert pid.product == product
    def test_extension(self):
        for spid in GOOD:
            extension = 'bar'
            pid = Pid('%s.%s' % (spid, extension))
            assert pid.extension == extension
    def test_tpe(self):
        for spid in GOOD:
            t, p, e = 927, 'baz', 'quux'
            pid = Pid('%s_%05d_%s.%s' % (spid, t, p, e))
            assert pid.target == t, 'target wrong'
            assert pid.product == p, 'product wrong'
            assert pid.extension == e, 'extension wrong'
    def test_set_target(self):
        for spid in GOOD:
            pid, target = Pid(spid), 7
            pid.target = target
            assert pid.pid == '%s_%05d' % (spid, target)
    def test_set_product(self):
        for spid in GOOD:
            pid, product = Pid(spid), 'foo'
            pid.product = product
            assert pid.pid == '%s_%s' % (spid, product)
    def test_set_extension(self):
        for spid in GOOD:
            pid, extension = Pid(spid), 'foo'
            pid.extension = extension
            assert pid.pid == '%s.%s' % (spid, extension)
    def test_set_spe(self):
        for spid in GOOD:
            pid = Pid(spid)
            t, p, e = 1, 'foo', 'bar'
            pid.target = t
            pid.product = p
            pid.extension = e
            expected = '%s_%05d_%s.%s' % (spid, t, p, e)
            assert pid.pid == expected
    def test_eq(self):
        for spid in GOOD:
            assert Pid(spid) == Pid(spid)
            assert Pid(spid) == spid
    def test_ne(self):
        for spid in GOOD:
            diff = spid + '.foo'
            assert Pid(spid) != Pid(diff)
            assert Pid(spid) != diff
    def test_copy_unparsed(self):
        for spid in GOOD:
            # create invalid, unparsed pid
            pid = Pid('_' + spid, parse=False)
            # copy it
            copy = pid.copy()
            # now parse it, expecting ValueError
            with self.assertRaises(ValueError):
                copy.parsed
    def test_copy(self):
        for spid in GOOD:
            pid = Pid(spid)
            copy = pid.copy()
            assert pid == copy

class TestV1Identifiers(unittest.TestCase):
    def test_timestamp_validation(self):
        with self.assertRaises(ValueError):
            ids.parse('IFCB1_2000_999_000000')
        with self.assertRaises(ValueError):
            ids.parse('IFCB1_2000_001_990000')
        with self.assertRaises(ValueError):
            ids.parse('IFCB1_2000_001_009900')
        with self.assertRaises(ValueError):
            ids.parse('IFCB1_2000_001_000099')
    def test_instrument(self):
        assert Pid(GOOD_V1).instrument == 1
    def test_day_prefix(self):
        assert Pid(GOOD_V1).day_prefix == 'IFCB1_2000_001'

class TestV2Identifiers(unittest.TestCase):
    def test_timestamp_validation(self):
        with self.assertRaises(ValueError):
            ids.parse('D20009901T000000_IFCB001')
        with self.assertRaises(ValueError):
            ids.parse('D20000199T000000_IFCB001')
        with self.assertRaises(ValueError):
            ids.parse('D20000101T990000_IFCB001')
        with self.assertRaises(ValueError):
            ids.parse('D20000101T009900_IFCB001')
        with self.assertRaises(ValueError):
            ids.parse('D20000101T000099_IFCB001')
    def test_instrument(self):
        assert Pid(GOOD_V2).instrument == 1
    def test_day_prefix(self):
        assert Pid(GOOD_V2).day_prefix == 'D20000101'
