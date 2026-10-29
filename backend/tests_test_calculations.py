"""Pruebas mínimas ejecutables con: python -m unittest discover -s . -p 'tests_*.py'"""
import unittest
from app.grade_calculator import systematic_average, calculate_cut, calculate_final, calculate_record

class GradeCalculatorTests(unittest.TestCase):
    def test_example(self):
        result = calculate_record([8, 8], 7, 9)
        self.assertEqual(result["systematic_average"], 8)
        self.assertEqual(result["cut1"], 7.5)
        self.assertEqual(result["cut2"], 8.5)
        self.assertEqual(result["final_40"], 32)
    def test_empty_is_none(self):
        self.assertIsNone(systematic_average([]))
    def test_missing_partial_means_pending(self):
        result = calculate_record([8], 7, None)
        self.assertIsNone(result["cut2"])
        self.assertIsNone(result["final_40"])
    def test_invalid_grade(self):
        with self.assertRaises(ValueError):
            systematic_average([11])
    def test_final_scale(self):
        self.assertEqual(calculate_final(10, 10), 40)

if __name__ == "__main__":
    unittest.main()
