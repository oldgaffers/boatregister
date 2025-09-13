import unittest
from src.util.format import (
    ONE_FOOT, format_designer_builder, price, m2dfn, m2df, feet, squarefeet, kg,
    m2f, m2f2, m2dsqf, m2dsqfn, f2m, f2m2, boatm2f, boatf2m, boat_defined, m2fall, newest_for_sale_record
)

class TestFormatUtils(unittest.TestCase):
    def test_f2m(self):
        self.assertAlmostEqual(f2m(10), round(1000 * ONE_FOOT * 10) / 1000)
        self.assertIsNone(f2m(None))

    def test_f2m2(self):
        self.assertAlmostEqual(f2m2(10), round(1000 * ONE_FOOT * ONE_FOOT * 10) / 1000)
        self.assertIsNone(f2m2(None))

    def test_m2dfn(self):
        self.assertAlmostEqual(m2dfn(3.048), 10.0)
        self.assertIsNone(m2dfn(None))

    def test_m2df(self):
        self.assertEqual(m2df(3.048), "10.00")
        self.assertIsNone(m2df(None))

    def test_feet(self):
        self.assertEqual(feet(10), "10.00 ft")

    def test_squarefeet(self):
        self.assertEqual(squarefeet(10), "10.00 ft²")

    def test_kg(self):
        self.assertEqual(kg(10.7), "10 kg")
        self.assertIsNone(kg(None))

    def test_m2f(self):
        self.assertEqual(m2f(3.048), "10.00 ft")
        self.assertIsNone(m2f(None))

    def test_m2f2(self):
        self.assertEqual(m2f2(9.290304), "10.00 ft²")
        self.assertIsNone(m2f2(None))

    def test_m2dsqf(self):
        self.assertEqual(m2dsqf(9.290304), "10.000")
        self.assertIsNone(m2dsqf(None))

    def test_m2dsqfn(self):
        self.assertEqual(m2dsqfn(9.290304), 10.0)
        self.assertIsNone(m2dsqfn(None))

    def test_price(self):
        self.assertEqual(price(0), "offers")
        self.assertEqual(price(1234.56), "£1,234.56")

    def test_format_designer_builder(self):
        self.assertEqual(format_designer_builder({'designer': {'name': 'John'}}, 'designer'), 'John')
        self.assertEqual(format_designer_builder({'designer': [{'name': 'John'}, {'name': 'Jane'}]}, 'designer'), 'John / Jane')
        self.assertIsNone(format_designer_builder({}, 'designer'))

    def test_boatm2f_and_boatf2m(self):
        boat = {'beam': 3.048, 'sailarea': 9.290304, 'year_is_approximate': True}
        m2f_boat = boatm2f(boat)
        self.assertEqual(m2f_boat['beam'], 10.0)
        self.assertEqual(m2f_boat['sailarea'], 10.0)
        self.assertTrue(m2f_boat['year_is_approximate'])
        # boatf2m returns boatm2f for lists
        self.assertEqual(boatf2m([boat])[0]['beam'], 10.0)

    def test_boat_defined(self):
        self.assertFalse(boat_defined(False))
        self.assertIsNone(boat_defined(None))
        self.assertIsNone(boat_defined([]))
        self.assertEqual(boat_defined([1, None, 2]), [1, 2])
        self.assertEqual(boat_defined({'a': 1, 'b': None}), {'a': 1})

    def test_m2fall(self):
        self.assertEqual(m2fall({'beam': 3.048, 'draft': 1.524}), [10.0, 5.0])
        self.assertIsNone(m2fall(None))

    def test_newest_for_sale_record(self):
        boat = {'for_sales': [
            {'created_at': '2020-01-01T00:00:00Z'},
            {'created_at': '2022-01-01T00:00:00Z'},
            {'created_at': '2021-01-01T00:00:00Z'}
        ]}
        self.assertEqual(newest_for_sale_record(boat)['created_at'], '2022-01-01T00:00:00Z')
        self.assertEqual(newest_for_sale_record({})['created_at'], '1970-01-01T00:00:00Z')

if __name__ == "__main__":
    unittest.main()
