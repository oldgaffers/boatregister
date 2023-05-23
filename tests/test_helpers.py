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
