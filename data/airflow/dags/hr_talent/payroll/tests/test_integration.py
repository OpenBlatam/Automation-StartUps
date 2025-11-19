"""
Tests de Integración para Sistema de Nómina
Tests end-to-end del sistema completo
"""

import unittest
from datetime import date, timedelta
from decimal import Decimal

from payroll import (
    PayrollStorage,
    HourCalculator,
    DeductionCalculator,
    PaymentCalculator,
    PayrollTestData,
    PayrollTestHelpers,
    get_pay_period_dates
)


class TestPayrollIntegration(unittest.TestCase):
    """Tests de integración del sistema de nómina"""
    
    def setUp(self):
        """Setup para tests"""
        self.storage = PayrollStorage()
        self.hour_calc = HourCalculator()
        self.deduction_calc = DeductionCalculator()
        self.payment_calc = PaymentCalculator(self.hour_calc, self.deduction_calc)
        
        # Crear datos de prueba
        self.test_employee = PayrollTestData.create_test_employee(
            "TEST_EMP_001",
            "Test Employee",
            Decimal("25.00"),
            "hourly"
        )
        
        period_start, period_end = get_pay_period_dates(period_type="biweekly")
        self.period_start = period_start
        self.period_end = period_end
    
    def test_complete_payroll_flow(self):
        """Test del flujo completo de nómina"""
        # Crear entradas de tiempo
        time_entries = PayrollTestData.create_test_time_entries(
            self.test_employee["employee_id"],
            self.period_start,
            self.period_end,
            hours_per_day=Decimal("8.0")
        )
        
        # Calcular horas
        hours_breakdown = self.hour_calc.calculate_overtime(
            time_entries,
            self.period_start,
            self.period_end
        )
        
        self.assertGreater(hours_breakdown["total_hours"], Decimal("0.00"))
        
        # Calcular deducciones
        deductions = self.deduction_calc.calculate_deductions(
            self.test_employee["employee_id"],
            Decimal("2000.00"),  # Gross pay
            {}
        )
        
        self.assertIsInstance(deductions, list)
        
        # Calcular pago completo
        calculation = self.payment_calc.calculate_pay_period(
            employee_id=self.test_employee["employee_id"],
            hourly_rate=self.test_employee["hourly_rate"],
            employee_type=self.test_employee["employee_type"],
            period_start=self.period_start,
            period_end=self.period_end,
            pay_date=self.period_end + timedelta(days=7),
            time_entries=time_entries,
            expenses_total=Decimal("100.00"),
            employee_context={}
        )
        
        # Validar cálculo
        PayrollTestHelpers.assert_calculation_valid(calculation)
        
        self.assertGreater(calculation.net_pay, Decimal("0.00"))
        self.assertEqual(calculation.employee_id, self.test_employee["employee_id"])
    
    def test_overtime_calculation(self):
        """Test de cálculo de overtime"""
        # Crear entradas con overtime
        time_entries = PayrollTestData.create_test_time_entries(
            self.test_employee["employee_id"],
            self.period_start,
            self.period_end,
            hours_per_day=Decimal("10.0"),  # Más de 8 horas
            include_overtime=True
        )
        
        hours_breakdown = self.hour_calc.calculate_overtime(
            time_entries,
            self.period_start,
            self.period_end
        )
        
        self.assertGreater(hours_breakdown["total_hours"], Decimal("0.00"))
    
    def test_deduction_calculation(self):
        """Test de cálculo de deducciones"""
        gross_pay = Decimal("5000.00")
        
        deductions = self.deduction_calc.calculate_deductions(
            self.test_employee["employee_id"],
            gross_pay,
            {
                "tax_rate": Decimal("0.25"),
                "benefits_rate": Decimal("0.10")
            }
        )
        
        total_deductions = sum(d.amount for d in deductions)
        
        self.assertGreater(total_deductions, Decimal("0.00"))
        self.assertLess(total_deductions, gross_pay)
    
    def test_validation(self):
        """Test de validaciones"""
        # Crear cálculo de prueba
        calculation = PayrollTestData.create_test_calculation(
            self.test_employee["employee_id"],
            self.period_start,
            self.period_end
        )
        
        # Validar
        PayrollTestHelpers.assert_calculation_valid(calculation)
        
        # Test de cálculo inválido (debería fallar)
        invalid_calculation = calculation
        invalid_calculation.net_pay = Decimal("-100.00")
        
        with self.assertRaises(AssertionError):
            PayrollTestHelpers.assert_calculation_valid(invalid_calculation)


if __name__ == "__main__":
    unittest.main()

