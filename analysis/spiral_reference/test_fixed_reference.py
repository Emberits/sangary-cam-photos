import json
import unittest
from pathlib import Path
from fixed_reference import measure


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(Path(__file__).with_name("reference.json").read_text())

    def run_measure(self, width=1.511, **kwargs):
        args = dict(registered=True, contour_valid=True, local_geometry_verified=True)
        args.update(kwargs)
        return measure(self.config, "upper", 1, width, **args)

    def test_zero(self):
        self.assertEqual(self.run_measure()["diameter_increase_mm"], 0)

    def test_known_increase(self):
        result = self.run_measure(1.511 + 3.840)
        self.assertAlmostEqual(result["diameter_increase_mm"], 130)
        self.assertAlmostEqual(result["symmetric_equivalent_mm"], 65)

    def test_negative_preserved(self):
        result = self.run_measure(1.0)
        self.assertLess(result["diameter_increase_mm"], 0)
        self.assertEqual(result["status"], "below_reference")

    def test_registration_gate(self):
        with self.assertRaises(ValueError):
            self.run_measure(registered=False)

    def test_contour_gate(self):
        with self.assertRaises(ValueError):
            self.run_measure(contour_valid=False)

    def test_geometry_gate(self):
        with self.assertRaises(ValueError):
            self.run_measure(local_geometry_verified=False)

    def test_no_cross_conductor_transfer(self):
        with self.assertRaises(ValueError):
            measure(self.config, "lower", 1, 2, registered=True,
                    contour_valid=True, local_geometry_verified=True)

    def test_nonfinite(self):
        with self.assertRaises(ValueError):
            self.run_measure(float("nan"))


if __name__ == "__main__":
    unittest.main()
