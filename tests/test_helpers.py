import os
import sys
# ensure repository root is on sys.path so imports work when running this script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers  import merge_object

class TestMain:

	def test_merge_object(self):
		existing = { 'name': 'None'}
		changes = { 'name': 'Robinetta'}
		assert merge_object(existing, changes) == changes
		changes = { 'oga_no': 315 }
		assert merge_object(existing, changes) == {**existing, **changes}
		changes = { 'oga_no': 315, 'generic_type': 'Pocket Cruiser' }
		assert merge_object(existing, changes) == {**existing, **changes}
