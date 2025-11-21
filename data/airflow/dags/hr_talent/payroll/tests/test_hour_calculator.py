"""
Tests para HourCalculator
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from payroll.hour_calculator import HourCalculator, TimeEntry, HoursType
from payroll.exceptions import ValidationError


class TestHourCalculator:
    """Tests para HourCalculator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.calculator = HourCalculator(
            regular_hours_per_week=Decimal("40.0"),
            overtime_multiplier=Decimal("1.5"),
            double_time_multiplier=Decimal("2.0")
        )
    
    def test_calculate_hours_from_timestamps(self):
        """Test cálculo de horas desde timestamps"""
        clock_in = datetime(2025, 1, 1, 9, 0)
        clock_out = datetime(2025, 1, 1, 17, 30)
        
        hours = self.calculator.calculate_hours_from_timestamps(clock_in, clock_out)
        
        assert hours == Decimal("8.50")
    
    def test_calculate_hours_invalid_timestamps(self):
        """Test que timestamps inválidos lanzan error"""
        clock_in = datetime(2025, 1, 1, 17, 0)
        clock_out = datetime(2025, 1, 1, 9, 0)
        
        with pytest.raises(ValidationError):
            self.calculator.calculate_hours_from_timestamps(clock_in, clock_out)
    
    def test_calculate_hours_exceeds_24(self):
        """Test que horas > 24 lanzan error"""
        clock_in = datetime(2025, 1, 1, 0, 0)
        clock_out = datetime(2025, 1, 2, 1, 0)  # 25 horas
        
        with pytest.raises(ValidationError):
            self.calculator.calculate_hours_from_timestamps(clock_in, clock_out)
    
    def test_calculate_overtime(self):
        """Test cálculo de overtime"""
        time_entries = [
            TimeEntry(
                employee_id="EMP001",
                work_date=date(2025, 1, 1),
                hours_worked=Decimal("45.0"),  # 5 horas extra
                hours_type=HoursType.REGULAR,
                hourly_rate=Decimal("25.00")
            )
        ]
        
        breakdown = self.calculator.calculate_overtime(
            time_entries,
            date(2025, 1, 1),
            date(2025, 1, 7)
        )
        
        assert breakdown["regular_hours"] == Decimal("40.00")
        assert breakdown["overtime_hours"] == Decimal("5.00")
    
    def test_calculate_total_hours(self):
        """Test cálculo de total de horas"""
        time_entries = [
            TimeEntry(
                employee_id="EMP001",
                work_date=date(2025, 1, 1),
                hours_worked=Decimal("8.0"),
                hours_type=HoursType.REGULAR,
                hourly_rate=Decimal("25.00")
            ),
            TimeEntry(
                employee_id="EMP001",
                work_date=date(2025, 1, 2),
                hours_worked=Decimal("8.0"),
                hours_type=HoursType.REGULAR,
                hourly_rate=Decimal("25.00")
            )
        ]
        
        total = self.calculator.calculate_total_hours(time_entries)
        
        assert total == Decimal("16.00")
    
    def test_validate_time_entry(self):
        """Test validación de entrada de tiempo"""
        entry = TimeEntry(
            employee_id="EMP001",
            work_date=date(2025, 1, 1),
            hours_worked=Decimal("8.0"),
            hours_type=HoursType.REGULAR,
            hourly_rate=Decimal("25.00")
        )
        
        is_valid, error = self.calculator.validate_time_entry(entry)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_time_entry_invalid(self):
        """Test validación de entrada inválida"""
        entry = TimeEntry(
            employee_id="EMP001",
            work_date=date(2025, 1, 1),
            hours_worked=Decimal("-5.0"),  # Negativo
            hours_type=HoursType.REGULAR,
            hourly_rate=Decimal("25.00")
        )
        
        is_valid, error = self.calculator.validate_time_entry(entry)
        
        assert is_valid is False
        assert error is not None

