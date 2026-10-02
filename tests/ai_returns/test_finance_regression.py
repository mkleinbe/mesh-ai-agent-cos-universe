import importlib.util
import math
from pathlib import Path
import unittest
PATH = Path(__file__).resolve().parents[2] / 'chatgpt/skills/mesh-cfo/scripts/financial_math.py'
SPEC = importlib.util.spec_from_file_location('finance', PATH)
finance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(finance)
class FinanceRegression(unittest.TestCase):
    def test_monthly_horizon(self):
        flows = [-10000] + [150] * 120
        self.assertAlmostEqual(finance.npv(finance.irr(flows), flows), 0, places=4)
    def test_nonconvergence(self):
        with self.assertRaises(finance.FinanceInputError): finance.irr([-100,110],max_iterations=1)
    def test_controls(self):
        for options in ({'tolerance':0},{'tolerance':True},{'max_iterations':True},{'max_iterations':0}):
            with self.assertRaises(finance.FinanceInputError): finance.irr([-100,110],**options)
    def test_ambiguity(self):
        with self.assertRaises(finance.FinanceInputError): finance.irr([-100,230,-132])
    def test_negative(self): self.assertAlmostEqual(finance.irr([-100,90]),-.1,places=8)
    def test_extreme(self):
        expected=math.exp((math.log(1e-308)-math.log(1e308))/100)-1
        self.assertAlmostEqual(finance.irr([-1e308]+[0]*99+[1e-308]),expected,places=9)
