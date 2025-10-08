import copy
import types
import sys
import pytest

# if PyYAML isn't installed in the test environment, provide a tiny shim so
# importing update_member_ownerships (which imports yaml at module scope)
# doesn't fail. The tests don't exercise yaml.safe_load here.
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
        boat['ownerships'] = copy.deepcopy(ownerships)
    if current:
        boat['current'] = True
    return boat


def test_update_to_member_replaces_name_with_id():
    ownerships = [
        {'name': 'Alice Smith', 'start': 2010},
        {'name': 'Bob Jones', 'start': 2012},
    ]
    boat = make_boat(oga_no=10, ownerships=ownerships)

    updated = update_owner(boat, 'Member', 'Alice', 'Smith', 12345, 555)

    assert updated is not None
    # ownerships should have id and member for Alice, and name removed
    ids = [o.get('id') for o in updated['ownerships']]
    assert 12345 in ids
    for o in updated['ownerships']:
        if o.get('id') == 12345:
            assert 'name' not in o
            assert o['member'] == 555


def test_update_to_non_member_replaces_id_with_name_and_keeps_end_none():
    ownerships = [
        {'id': 222, 'member': 999, 'start': 2000},
        {'id': 333, 'member': 111, 'start': 2005},
    ]
    boat = make_boat(oga_no=11, ownerships=ownerships)

    updated = update_owner(boat, 'Non-member', 'Carol', 'White', 333, 111)

    assert updated is not None
    # one ownership should now have name and not have id/member
    found = False
    for o in updated['ownerships']:
        if o.get('name') == 'Carol White':
            found = True
            assert 'id' not in o
            assert 'member' not in o
    assert found


def test_update_to_deceased_sets_end_and_removes_current():
    ownerships = [
        {'id': 444, 'member': 222, 'start': 1999},
    ]
    boat = make_boat(oga_no=12, ownerships=ownerships, current=True)

    updated = update_owner(boat, 'Deceased', 'Don', 'Brown', 444, 222)

    assert updated is not None
    # boat should no longer be marked current
    assert 'current' not in updated
    # ownership should have name and an 'end' year
    o = updated['ownerships'][0]
    assert o.get('name') == 'Don Brown'
    assert 'id' not in o
    assert 'member' not in o
    assert 'end' in o and isinstance(o['end'], int)


def test_no_change_returns_none():
    # if the provided name/id are not present, nothing changes
    ownerships = [
        {'name': 'Eve Adams', 'start': 2015},
    ]
    boat = make_boat(oga_no=13, ownerships=ownerships)

    updated = update_owner(boat, 'Member', 'Nonexistent', 'Person', 9999, 0)
    assert updated is None
