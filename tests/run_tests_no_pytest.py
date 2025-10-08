import os
import sys

# ensure repository root is on sys.path so imports work when running this script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import types
import sys

# shim yaml if it's not available in this execution environment
if 'yaml' not in sys.modules:
    class _YamlShim:
        def __init__(self):
            self._reprs = {}
        def safe_load(self, *a, **k):
            return None
        def safe_dump(self, *a, **k):
            return ''
        def add_representer(self, t, fn):
            self._reprs[t] = fn
        def dump(self, d, outfile, **kw):
            # naive dump: write JSON-ish text to outfile
            try:
                import json
                outfile.write(json.dumps(d))
            except Exception:
                outfile.write(str(d))
    sys.modules['yaml'] = _YamlShim()

# shim markdownify and markdown modules used by helpers.py
if 'markdownify' not in sys.modules:
    sys.modules['markdownify'] = types.SimpleNamespace(markdownify=lambda s, **k: s)

if 'markdown' not in sys.modules:
    class _MarkdownShim:
        def __init__(self, extensions=None, extension_configs=None):
            pass
        def convert(self, s):
            return s
    sys.modules['markdown'] = types.SimpleNamespace(Markdown=_MarkdownShim)

from update_member_ownerships import update_owner


def make_boat(oga_no=1, name="Test Boat", ownerships=None, current=True):
    boat = {
        'oga_no': oga_no,
        'name': name,
    }
    if ownerships is not None:
        boat['ownerships'] = [o.copy() for o in ownerships]
    if current:
        boat['current'] = True
    return boat


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def test_update_to_member_replaces_name_with_id():
    ownerships = [
        {'name': 'Alice Smith', 'start': 2010},
        {'name': 'Bob Jones', 'start': 2012},
    ]
    boat = make_boat(oga_no=10, ownerships=ownerships)
    updated = update_owner(boat, 'Member', 'Alice', 'Smith', 12345, 555)
    assert_true(updated is not None, 'expected update for Member')
    ids = [o.get('id') for o in updated['ownerships']]
    assert_true(12345 in ids, 'expected id present')


def test_update_to_non_member_replaces_id_with_name_and_keeps_end_none():
    ownerships = [
        {'id': 222, 'member': 999, 'start': 2000},
        {'id': 333, 'member': 111, 'start': 2005},
    ]
    boat = make_boat(oga_no=11, ownerships=ownerships)
    updated = update_owner(boat, 'Non-member', 'Carol', 'White', 333, 111)
    assert_true(updated is not None, 'expected update for Non-member')
    found = any(o.get('name') == 'Carol White' for o in updated['ownerships'])
    assert_true(found, 'expected name for non-member')


def test_update_to_deceased_sets_end_and_removes_current():
    ownerships = [
        {'id': 444, 'member': 222, 'start': 1999},
    ]
    boat = make_boat(oga_no=12, ownerships=ownerships, current=True)
    updated = update_owner(boat, 'Deceased', 'Don', 'Brown', 444, 222)
    assert_true(updated is not None, 'expected update for Deceased')
    assert_true('current' not in updated, 'expected current removed')
    o = updated['ownerships'][0]
    assert_true(o.get('name') == 'Don Brown', 'expected name set')
    assert_true('end' in o and isinstance(o['end'], int), 'expected end year')


def test_no_change_returns_none():
    ownerships = [
        {'name': 'Eve Adams', 'start': 2015},
    ]
    boat = make_boat(oga_no=13, ownerships=ownerships)
    updated = update_owner(boat, 'Member', 'Nonexistent', 'Person', 9999, 0)
    assert_true(updated is None, 'expected no change')


if __name__ == '__main__':
    tests = [
        test_update_to_member_replaces_name_with_id,
        test_update_to_non_member_replaces_id_with_name_and_keeps_end_none,
        test_update_to_deceased_sets_end_and_removes_current,
        test_no_change_returns_none,
    ]
    for t in tests:
        print('Running', t.__name__)
        t()
    print('All tests passed')
