"""
Tests para PaymentCalculator
Tests unitarios del módulo de cálculo de pagos
"""

import unittest
from datetime import date, timedelta
from decimal import Decimal

from payroll import (
    PaymentCalculator,
    HourCalculator,
    DeductionCalculator,
    PayPeriodCalculation,
    TimeEntry,
    HoursType
)
from payroll.testing import PayrollTestData, PayrollTestHelpers
from payroll.exceptions import ValidationError, CalculationError


class TestPaymentCalculator(unittest.TestCase):
    """Tests para PaymentCalculator"""
    
    def setUp(self):
        """Setup para tests"""
        self.hour_calc = HourCalculator()
        self.deduction_calc = DeductionCalculator()
        self.payment_calc = PaymentCalculator(self.hour_calc, self.deduction_calc)
        
        self.employee_id = "TEST_EMP_001"
        self.hourly_rate = Decimal("25.00")
        self.period_start = date(2025, 1, 1)
        self.period_end = date(2025, 1, 14)
        self.pay_date = date(2025, 1, 21)
    
    def test_calculate_pay_period_hourly(self):
        """Test cálculo de período para empleado hourly"""
        time_entries = PayrollTestData.create_test_time_entries(
            self.employee_id,
            self.period_start,
            self.period_end,
            hours_per_day=Decimal("8.0")
        )
        
        calculation = self.payment_calc.calculate_pay_period(
            employee_id=self.employee_id,
            hourly_rate=self.hourly_rate,
            employee_type="hourly",
            period_start=self.period_start,
            period_end=self.period_end,
            pay_date=self.pay_date,
            time_entries=time_entries,
            expenses_total=Decimal("100.00"),
            employee_context={}
        )
        
        # Validar
        PayrollTestHelpers.assert_calculation_valid(calculation)
        
        # Aserciones específicas
        self.assertGreater(calculation.gross_pay, Decimal("0.00"))
        self.assertGreater(calculation.net_pay, Decimal("0.00"))
        self.assertEqual(calculation.employee_id, self.employee_id)
    
    def test_calculate_pay_period_with_overtime(self):
        """Test cálculo con overtime"""
        time_entries = PayrollTestData.create_test_time_entries(
            self.employee_id,
            self.period_start,
            self.period_end,
            hours_per_day=Decimal("10.0"),  # Más de 8 horas
            include_overtime=True
        )
        
        calculation = self.payment_calc.calculate_pay_period(
            employee_id=self.employee_id,
            hourly_rate=self.hourly_rate,
            employee_type="hourly",
            period_start=self.period_start,
            period_end=self.period_end,
            pay_date=self.pay_date,
            time_entries=time_entries,
            expenses_total=Decimal("0.00"),
            employee_context={}
        )
        
        # Debe tener overtime
        self.assertGreater(calculation.overtime_hours, Decimal("0.00"))
        self.assertGreater(calculation.gross_pay, calculation.regular_hours * self.hourly_rate)
    
    def test_validate_calculation(self):
        """Test validación de cálculo"""
        # Crear cálculo válido
        calculation = PayrollTestData.create_test_calculation(
            self.employee_id,
            self.period_start,
            self.period_end
        )
        
        is_valid, error = self.payment_calc.validate_calculation(calculation)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Crear cálculo inválido (net pay negativo)
        invalid_calculation = calculation
        invalid_calculation.net_pay = Decimal("-100.00")
        
        is_valid, error = self.payment_calc.validate_calculation(invalid_calculation)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_calculation_with_expenses(self):
        """Test cálculo incluyendo gastos reembolsables"""
        time_entries = PayrollTestData.create_test_time_entries(
            self.employee_id,
            self.period_start,
            self.period_end
        )
        
        expenses_total = Decimal("500.00")
        
        calculation = self.payment_calc.calculate_pay_period(
            employee_id=self.employee_id,
            hourly_rate=self.hourly_rate,
            employee_type="hourly",
            period_start=self.period_start,
            period_end=self.period_end,
            pay_date=self.pay_date,
            time_entries=time_entries,
            expenses_total=expenses_total,
            employee_context={}
        )
        
        # Net pay debe incluir gastos
        expected_net = calculation.gross_pay - calculation.total_deductions + expenses_total
        self.assertAlmostEqual(
            float(calculation.net_pay),
            float(expected_net),
            places=2
        )


if __name__ == "__main__":
    unittest.main()

