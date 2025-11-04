import os
import sys
# ensure repository root is on sys.path so imports work when running this script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from merge_field import merge_field

class TestMain:

	def test_merge_field(self):
		assert merge_field('builder', 'x', ['y', 'z']) is None