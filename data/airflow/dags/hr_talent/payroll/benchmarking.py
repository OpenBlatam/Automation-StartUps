"""
Sistema de Benchmarking para Nómina
Benchmarking y performance testing
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Resultado de un benchmark"""
    name: str
    iterations: int
    total_time: float
    average_time: float
    median_time: float
    min_time: float
    max_time: float
    std_dev: float
    operations_per_second: float
    success_rate: float
    errors: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PayrollBenchmark:
    """Sistema de benchmarking para nómina"""
    
    def __init__(self):
        """Inicializa sistema de benchmarking"""
        self.results: List[BenchmarkResult] = []
    
    def benchmark_function(
        self,
        name: str,
        function: callable,
        iterations: int = 10,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Ejecuta benchmark de una función"""
        times = []
        errors = []
        successes = 0
        
        logger.info(f"Starting benchmark: {name} ({iterations} iterations)")
        
        for i in range(iterations):
            try:
                start_time = time.time()
                function(*args, **kwargs)
                elapsed = time.time() - start_time
                
                times.append(elapsed)
                successes += 1
                
            except Exception as e:
                error_msg = f"Iteration {i + 1} failed: {e}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        if not times:
            raise ValueError("All iterations failed")
        
        total_time = sum(times)
        average_time = mean(times)
        median_time = median(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = stdev(times) if len(times) > 1 else 0.0
        operations_per_second = iterations / total_time if total_time > 0 else 0.0
        success_rate = successes / iterations if iterations > 0 else 0.0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            average_time=average_time,
            median_time=median_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            operations_per_second=operations_per_second,
            success_rate=success_rate,
            errors=errors
        )
        
        self.results.append(result)
        
        logger.info(
            f"Benchmark completed: {name} - "
            f"Avg: {average_time:.4f}s, "
            f"Ops/sec: {operations_per_second:.2f}, "
            f"Success: {success_rate:.2%}"
        )
        
        return result
    
    def benchmark_storage_operations(
        self,
        storage,
        iterations: int = 10
    ) -> Dict[str, BenchmarkResult]:
        """Benchmark de operaciones de storage"""
        results = {}
        
        # Benchmark get_employee
        if hasattr(storage, 'get_employee'):
            results['get_employee'] = self.benchmark_function(
                "storage_get_employee",
                storage.get_employee,
                iterations,
                "TEST_EMP"
            )
        
        # Benchmark list_active_employees
        if hasattr(storage, 'list_active_employees'):
            results['list_active_employees'] = self.benchmark_function(
                "storage_list_active_employees",
                storage.list_active_employees,
                iterations
            )
        
        return results
    
    def benchmark_calculations(
        self,
        hour_calc,
        deduction_calc,
        payment_calc,
        iterations: int = 10
    ) -> Dict[str, BenchmarkResult]:
        """Benchmark de cálculos"""
        results = {}
        
        # Importar datos de prueba
        from .testing import PayrollTestData
        from datetime import date
        
        time_entries = PayrollTestData.create_test_time_entries(
            "TEST_EMP",
            date(2025, 1, 1),
            date(2025, 1, 14)
        )
        
        # Benchmark calculate_overtime
        results['calculate_overtime'] = self.benchmark_function(
            "hour_calculator_calculate_overtime",
            hour_calc.calculate_overtime,
            iterations,
            time_entries,
            date(2025, 1, 1),
            date(2025, 1, 14)
        )
        
        # Benchmark calculate_deductions
        results['calculate_deductions'] = self.benchmark_function(
            "deduction_calculator_calculate_deductions",
            deduction_calc.calculate_deductions,
            iterations,
            "TEST_EMP",
            5000.00,
            {}
        )
        
        return results
    
    def compare_results(
        self,
        result1: BenchmarkResult,
        result2: BenchmarkResult
    ) -> Dict[str, Any]:
        """Compara dos resultados de benchmark"""
        avg_diff = ((result2.average_time - result1.average_time) / result1.average_time) * 100
        ops_diff = ((result2.operations_per_second - result1.operations_per_second) / result1.operations_per_second) * 100
        
        return {
            "result1": result1.name,
            "result2": result2.name,
            "average_time_diff_percent": avg_diff,
            "operations_per_second_diff_percent": ops_diff,
            "faster": result1.name if result1.average_time < result2.average_time else result2.name,
            "improvement": abs(avg_diff)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de todos los benchmarks"""
        if not self.results:
            return {"error": "No benchmark results available"}
        
        total_benchmarks = len(self.results)
        total_time = sum(r.total_time for r in self.results)
        total_operations = sum(r.iterations for r in self.results)
        avg_success_rate = mean(r.success_rate for r in self.results)
        
        fastest = min(self.results, key=lambda x: x.average_time)
        slowest = max(self.results, key=lambda x: x.average_time)
        
        return {
            "total_benchmarks": total_benchmarks,
            "total_time": total_time,
            "total_operations": total_operations,
            "average_success_rate": avg_success_rate,
            "fastest": {
                "name": fastest.name,
                "average_time": fastest.average_time,
                "operations_per_second": fastest.operations_per_second
            },
            "slowest": {
                "name": slowest.name,
                "average_time": slowest.average_time,
                "operations_per_second": slowest.operations_per_second
            },
            "results": [
                {
                    "name": r.name,
                    "average_time": r.average_time,
                    "operations_per_second": r.operations_per_second,
                    "success_rate": r.success_rate
                }
                for r in self.results
            ]
        }
    
    def export_results(self, format: str = "json") -> str:
        """Exporta resultados de benchmarks"""
        import json
        
        if format == "json":
            results_data = [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "average_time": r.average_time,
                    "median_time": r.median_time,
                    "min_time": r.min_time,
                    "max_time": r.max_time,
                    "std_dev": r.std_dev,
                    "operations_per_second": r.operations_per_second,
                    "success_rate": r.success_rate,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results
            ]
            return json.dumps(results_data, indent=2)
        
        # CSV format
        elif format == "csv":
            lines = ["name,iterations,average_time,median_time,min_time,max_time,std_dev,ops_per_sec,success_rate"]
            for r in self.results:
                lines.append(
                    f"{r.name},{r.iterations},{r.average_time},{r.median_time},"
                    f"{r.min_time},{r.max_time},{r.std_dev},{r.operations_per_second},{r.success_rate}"
                )
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")

